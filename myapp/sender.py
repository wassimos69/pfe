#!/usr/bin/env python3
import argparse
import json
import os
import socket
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import hailo_platform as hp

CLASS_NAMES = ['ball', 'goalkeeper', 'player', 'referee']
BALL_CLASS_ID = 0
GOALKEEPER_CLASS_ID = 1
PLAYER_CLASS_ID = 2
REFEREE_CLASS_ID = 3

NUM_CLASSES_POSE = 1
NUM_KEYPOINTS = 32
REG_MAX = 15
POSE_INPUT_W = 640
POSE_INPUT_H = 640
POSE_CONF_THRESH = 0.25
POSE_NMS_IOU_THRESH = 0.70
POSE_KP_THRESH = 0.25
POSE_MAX_DETECTIONS = 1
KPT_SMOOTH_ALPHA = 0.55
KPT_MAX_JUMP = 80.0
KPT_HOLD_FRAMES = 12

DET_CONF_TH = 0.25
BALL_CONF_TH = 0.08
DET_IOU_TH = 0.45
MODEL_INPUT_SIZE = 640

KEYPOINT_CLASS_TO_LABEL = [
    1, 2, 3, 4, 5, 6, 7, 8,
    9, 10, 11, 12, 13, 15, 16, 17,
    18, 20, 21, 22, 23, 24, 25, 26,
    27, 28, 29, 30, 31, 32, 14, 19,
]


def sigmoid(x):
    x = np.clip(x, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-x))


def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.maximum(np.sum(e, axis=axis, keepdims=True), 1e-9)


def dequantize(arr, qp_scale, qp_zp):
    return qp_scale * (arr.astype(np.float32) - qp_zp)


def to_nc(t):
    a = np.asarray(t)

    if a.ndim >= 1 and a.shape[0] == 1:
        a = np.squeeze(a, axis=0)
    else:
        a = np.squeeze(a)

    if a.ndim == 0:
        return np.asarray([[float(a)]], dtype=np.float32)

    if a.ndim == 1:
        return a.astype(np.float32).reshape(-1, 1)

    if a.ndim == 2:
        r, c = a.shape
        if r <= 256 and c > r:
            return a.T.astype(np.float32)
        return a.astype(np.float32)

    if a.ndim == 3:
        s = a.shape
        if s[-1] <= 256 and (s[0] * s[1]) >= s[-1]:
            return a.reshape(-1, s[-1]).astype(np.float32)
        if s[0] <= 256 and (s[1] * s[2]) >= s[0]:
            return np.moveaxis(a, 0, -1).reshape(-1, s[0]).astype(np.float32)
        cax = int(np.argmin(s))
        if cax != 2:
            a = np.moveaxis(a, cax, 2)
        return a.reshape(-1, a.shape[2]).astype(np.float32)

    if a.ndim == 4:
        s = a.shape
        if s[-1] <= 256:
            return a.reshape(-1, s[-1]).astype(np.float32)
        if s[1] <= 256:
            return np.moveaxis(a, 1, -1).reshape(-1, s[1]).astype(np.float32)

    c = a.shape[-1]
    return a.reshape(-1, c).astype(np.float32)


def letterbox(image, new_shape=(640, 640), color=(114, 114, 114)):
    h, w = image.shape[:2]
    new_w, new_h = new_shape

    r = min(new_w / w, new_h / h)
    resized_w = int(round(w * r))
    resized_h = int(round(h * r))

    resized = cv2.resize(image, (resized_w, resized_h), interpolation=cv2.INTER_LINEAR)

    dw = new_w - resized_w
    dh = new_h - resized_h

    left = dw // 2
    right = dw - left
    top = dh // 2
    bottom = dh - top

    padded = cv2.copyMakeBorder(
        resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return padded, r, left, top


def resize_frame_for_inference(image, size=MODEL_INPUT_SIZE):
    h, w = image.shape[:2]
    if (w, h) == (size, size):
        return image.copy(), 1.0, 1.0
    resized = cv2.resize(image, (size, size), interpolation=cv2.INTER_LINEAR)
    return resized, w / float(size), h / float(size)


def scale_dets_from_resized_frame(dets, sx, sy, orig_w, orig_h):
    if len(dets) == 0:
        return dets
    out = dets.copy()
    out[:, [0, 2]] *= sx
    out[:, [1, 3]] *= sy
    out[:, [0, 2]] = np.clip(out[:, [0, 2]], 0, orig_w - 1)
    out[:, [1, 3]] = np.clip(out[:, [1, 3]], 0, orig_h - 1)
    return out


def preprocess_stretch_uint8(image, new_shape=(640, 640), bgr_to_rgb=True):
    new_w, new_h = new_shape
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    if bgr_to_rgb:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(resized, dtype=np.uint8)


def scale_xyxy_from_letterbox(xyxy, scale, pad_x, pad_y, orig_w, orig_h):
    out = np.array(xyxy, dtype=np.float32).copy()
    out[:, [0, 2]] = (out[:, [0, 2]] - pad_x) / scale
    out[:, [1, 3]] = (out[:, [1, 3]] - pad_y) / scale
    out[:, [0, 2]] = np.clip(out[:, [0, 2]], 0, orig_w - 1)
    out[:, [1, 3]] = np.clip(out[:, [1, 3]], 0, orig_h - 1)
    return out


def scale_xyxy_from_stretch(xyxy, sx, sy, orig_w, orig_h):
    out = np.array(xyxy, dtype=np.float32).copy()
    out[:, [0, 2]] *= sx
    out[:, [1, 3]] *= sy
    out[:, [0, 2]] = np.clip(out[:, [0, 2]], 0, orig_w - 1)
    out[:, [1, 3]] = np.clip(out[:, [1, 3]], 0, orig_h - 1)
    return out


def remap_keypoints_to_semantic_with_conf(points):
    remapped = {}
    for class_id, value in points.items():
        if 0 <= class_id < len(KEYPOINT_CLASS_TO_LABEL):
            semantic_id = KEYPOINT_CLASS_TO_LABEL[class_id] - 1
            remapped[semantic_id] = value
    return remapped


class KeypointStabilizer:
    def __init__(self, alpha=KPT_SMOOTH_ALPHA, max_jump=KPT_MAX_JUMP, hold_frames=KPT_HOLD_FRAMES):
        self.alpha = float(alpha)
        self.max_jump = float(max_jump)
        self.hold_frames = int(hold_frames)
        self.points = {}
        self.age = {}

    def update(self, keypoints_conf):
        if not keypoints_conf:
            return self._held_points()

        updated = {}
        seen = set()

        for k, value in keypoints_conf.items():
            x, y, conf = value
            k = int(k)
            current = np.array([float(x), float(y)], dtype=np.float32)
            prev = self.points.get(k)

            if prev is not None:
                prev_xy = np.array(prev[:2], dtype=np.float32)
                jump = float(np.linalg.norm(current - prev_xy))
                if self.max_jump > 0.0 and jump > self.max_jump:
                    updated[k] = prev
                    self.age[k] = min(self.age.get(k, 0) + 1, self.hold_frames + 1)
                    seen.add(k)
                    continue

                smooth_xy = (1.0 - self.alpha) * prev_xy + self.alpha * current
                smooth_conf = max(float(conf), float(prev[2]) * 0.95)
                out = (float(smooth_xy[0]), float(smooth_xy[1]), float(smooth_conf))
            else:
                out = (float(x), float(y), float(conf))

            self.points[k] = out
            self.age[k] = 0
            updated[k] = out
            seen.add(k)

        for k in list(self.points.keys()):
            if k in seen:
                continue
            self.age[k] = self.age.get(k, 0) + 1
            if self.age[k] <= self.hold_frames:
                updated[k] = self.points[k]
            else:
                self.points.pop(k, None)
                self.age.pop(k, None)

        return updated

    def _held_points(self):
        held = {}
        for k in list(self.points.keys()):
            self.age[k] = self.age.get(k, 0) + 1
            if self.age[k] <= self.hold_frames:
                held[k] = self.points[k]
            else:
                self.points.pop(k, None)
                self.age.pop(k, None)
        return held


def decode_dfl(dfl64):
    d = dfl64[:, :64].reshape(-1, 4, 16)
    bins = np.arange(16, dtype=np.float32)[None, None, :]
    return np.sum(softmax(d, axis=2) * bins, axis=2)


def infer_stride(in_w, n):
    mapping = {6400: 8, 1600: 16, 400: 32}
    if n in mapping:
        return mapping[n], int(round(np.sqrt(n)))
    side = int(round(np.sqrt(n)))
    if side * side == n and side > 0:
        return max(1, in_w // side), side
    return 0, 0


def decode_detector(
    outputs_dict,
    in_wh,
    orig_wh,
    conf_th=0.25,
    iou_th=0.45,
    ball_conf_th=0.08,
    scale_info: Optional[Tuple[str, float, float, float]] = None,
):
    in_w, in_h = in_wh
    orig_w, orig_h = orig_wh

    groups = {}
    for _, t in outputs_dict.items():
        mat = to_nc(t)
        n, c = mat.shape
        g = groups.setdefault(n, {})
        if c >= 64 and 'dfl' not in g:
            g['dfl'] = mat[:, :64]
        elif 'cls' not in g:
            g['cls'] = mat

    boxes, scores, class_ids = [], [], []

    for n, g in sorted(groups.items(), key=lambda kv: kv[0], reverse=True):
        if 'dfl' not in g or 'cls' not in g:
            continue

        stride, side = infer_stride(in_w, n)
        if stride <= 0 or side <= 0:
            continue

        dist = decode_dfl(g['dfl'])
        cls = g['cls']
        cls_logits = cls[:, :len(CLASS_NAMES)] if cls.shape[1] >= len(CLASS_NAMES) else cls

        if np.min(cls_logits) < 0.0 or np.max(cls_logits) > 1.0:
            conf = sigmoid(cls_logits)
        else:
            conf = cls_logits

        if conf.ndim == 1:
            conf = conf[:, None]

        best_cls = np.argmax(conf, axis=1)
        best_score = conf[np.arange(conf.shape[0]), best_cls]
        ball_score = conf[:, BALL_CLASS_ID] if conf.shape[1] > BALL_CLASS_ID else np.zeros_like(best_score)

        keep_best = best_score >= conf_th
        keep_ball = ball_score >= ball_conf_th
        if not np.any(keep_best) and not np.any(keep_ball):
            continue

        gy, gx = np.divmod(np.arange(n), side)
        cx = (gx.astype(np.float32) + 0.5) * stride
        cy = (gy.astype(np.float32) + 0.5) * stride

        l = dist[:, 0] * stride
        t = dist[:, 1] * stride
        r = dist[:, 2] * stride
        b = dist[:, 3] * stride

        decoded = np.stack([cx - l, cy - t, cx + r, cy + b], axis=1).astype(np.float32)
        if scale_info is not None and scale_info[0] == "letterbox":
            decoded = scale_xyxy_from_letterbox(decoded, scale_info[1], scale_info[2], scale_info[3], orig_w, orig_h)
        elif scale_info is not None and scale_info[0] == "stretch":
            decoded = scale_xyxy_from_stretch(decoded, scale_info[1], scale_info[2], orig_w, orig_h)
        else:
            sx = orig_w / float(in_w)
            sy = orig_h / float(in_h)
            decoded = scale_xyxy_from_stretch(decoded, sx, sy, orig_w, orig_h)

        x1, y1, x2, y2 = decoded[:, 0], decoded[:, 1], decoded[:, 2], decoded[:, 3]

        candidate_rows = []
        for i in np.where(keep_best)[0]:
            candidate_rows.append((int(i), int(best_cls[i]), float(best_score[i])))
        for i in np.where(keep_ball)[0]:
            if int(best_cls[i]) == BALL_CLASS_ID:
                continue
            candidate_rows.append((int(i), BALL_CLASS_ID, float(ball_score[i])))

        for i, cid, score in candidate_rows:
            if cid >= len(CLASS_NAMES):
                cid = len(CLASS_NAMES) - 1
            boxes.append([float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i])])
            scores.append(score)
            class_ids.append(cid)

    if not boxes:
        return []

    idx = []
    class_ids_np = np.array(class_ids, dtype=np.int32)
    for cls_id in sorted(set(class_ids)):
        cls_indices = np.where(class_ids_np == int(cls_id))[0]
        cls_boxes = [boxes[i] for i in cls_indices]
        cls_scores = [scores[i] for i in cls_indices]
        cls_xywh = [[b[0], b[1], max(1.0, b[2] - b[0]), max(1.0, b[3] - b[1])] for b in cls_boxes]
        cls_th = ball_conf_th if int(cls_id) == BALL_CLASS_ID else conf_th
        kept = cv2.dnn.NMSBoxes(cls_xywh, cls_scores, cls_th, iou_th)
        if len(kept):
            idx.extend([int(cls_indices[j]) for j in kept.flatten().tolist()])

    return [{'box': boxes[i], 'score': scores[i], 'class_id': class_ids[i]} for i in idx]


def iou_xyxy(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter = inter_w * inter_h

    area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union = area1 + area2 - inter + 1e-6

    return inter / union


def nms_pose(boxes, scores, iou_thresh=0.7, max_det=1):
    if len(boxes) == 0:
        return []

    order = np.argsort(scores)[::-1]
    keep = []

    while len(order) > 0 and len(keep) < max_det:
        i = order[0]
        keep.append(i)

        if len(order) == 1:
            break

        rest = order[1:]
        remain = []

        for j in rest:
            if iou_xyxy(boxes[i], boxes[j]) < iou_thresh:
                remain.append(j)

        order = np.array(remain, dtype=np.int64)

    return keep


def decode_boxes_dfl(box_tensor, stride, reg_max=15):
    h, w, c = box_tensor.shape
    box_tensor = box_tensor.reshape(h, w, 4, reg_max + 1)
    prob = softmax(box_tensor, axis=-1)
    proj = np.arange(reg_max + 1, dtype=np.float32)
    dist = np.sum(prob * proj, axis=-1) * stride

    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    center_x = (grid_x.astype(np.float32) + 0.5) * stride
    center_y = (grid_y.astype(np.float32) + 0.5) * stride
    centers_xy = np.stack([center_x, center_y], axis=-1).reshape(-1, 2)

    dist = dist.reshape(-1, 4)

    x1 = centers_xy[:, 0] - dist[:, 0]
    y1 = centers_xy[:, 1] - dist[:, 1]
    x2 = centers_xy[:, 0] + dist[:, 2]
    y2 = centers_xy[:, 1] + dist[:, 3]

    boxes = np.stack([x1, y1, x2, y2], axis=1)
    return boxes, centers_xy


def decode_keypoints(kpt_tensor, centers_xy, stride, num_keypoints=32):
    h, w, c = kpt_tensor.shape
    kpt = kpt_tensor.reshape(h * w, num_keypoints, 3).astype(np.float32)

    raw_xy = kpt[..., :2]
    raw_score = kpt[..., 2:3]

    xy = stride * (raw_xy * 2.0 - 0.5) + centers_xy[:, None, :]
    score = sigmoid(raw_score)

    return np.concatenate([xy, score], axis=-1)


def decode_single_scale(box_tensor, cls_tensor, kpt_tensor, stride):
    boxes, centers_xy = decode_boxes_dfl(box_tensor, stride, reg_max=REG_MAX)
    scores = cls_tensor.reshape(-1, NUM_CLASSES_POSE).astype(np.float32).squeeze(-1)
    keypoints = decode_keypoints(kpt_tensor, centers_xy, stride, num_keypoints=NUM_KEYPOINTS)
    return boxes, scores, keypoints


def transpose_if_needed(arr, target_hwc):
    if arr.shape == target_hwc:
        return arr

    h, w, c = target_hwc

    if arr.shape == (c, h, w):
        return np.transpose(arr, (1, 2, 0))

    if len(arr.shape) == 4 and arr.shape[0] == 1:
        arr = arr[0]
        if arr.shape == target_hwc:
            return arr
        if arr.shape == (c, h, w):
            return np.transpose(arr, (1, 2, 0))

    raise ValueError(f"Cannot convert shape {arr.shape} to target {target_hwc}")


def map_outputs_by_shape(outputs_dict):
    mapped = {}
    targets = [
        ("80_box", (80, 80, 64)),
        ("80_cls", (80, 80, 1)),
        ("80_kpt", (80, 80, 96)),
        ("40_box", (40, 40, 64)),
        ("40_cls", (40, 40, 1)),
        ("40_kpt", (40, 40, 96)),
        ("20_box", (20, 20, 64)),
        ("20_cls", (20, 20, 1)),
        ("20_kpt", (20, 20, 96)),
    ]

    used = set()

    for key, target_shape in targets:
        found_name = None
        found_arr = None

        for name, arr in outputs_dict.items():
            if name in used:
                continue
            try:
                arr_hwc = transpose_if_needed(arr, target_shape)
                found_name = name
                found_arr = arr_hwc
                break
            except Exception:
                continue

        if found_arr is None:
            raise RuntimeError(f"Impossible de mapper {key} vers {target_shape}")

        mapped[key] = found_arr
        used.add(found_name)

    return mapped


def scale_coords_back_letterbox(boxes, keypoints, scale, pad_x, pad_y, orig_w, orig_h):
    boxes_out = boxes.copy()
    kpts_out = keypoints.copy()

    boxes_out[:, [0, 2]] = (boxes_out[:, [0, 2]] - pad_x) / scale
    boxes_out[:, [1, 3]] = (boxes_out[:, [1, 3]] - pad_y) / scale

    kpts_out[..., 0] = (kpts_out[..., 0] - pad_x) / scale
    kpts_out[..., 1] = (kpts_out[..., 1] - pad_y) / scale

    boxes_out[:, [0, 2]] = np.clip(boxes_out[:, [0, 2]], 0, orig_w - 1)
    boxes_out[:, [1, 3]] = np.clip(boxes_out[:, [1, 3]], 0, orig_h - 1)

    return boxes_out, kpts_out


def scale_coords_back_stretch(boxes, keypoints, sx, sy, orig_w, orig_h):
    boxes_out = boxes.copy()
    kpts_out = keypoints.copy()

    boxes_out[:, [0, 2]] *= sx
    boxes_out[:, [1, 3]] *= sy

    kpts_out[..., 0] *= sx
    kpts_out[..., 1] *= sy

    boxes_out[:, [0, 2]] = np.clip(boxes_out[:, [0, 2]], 0, orig_w - 1)
    boxes_out[:, [1, 3]] = np.clip(boxes_out[:, [1, 3]], 0, orig_h - 1)

    return boxes_out, kpts_out


def decode_pose_outputs(
    outputs,
    quant_info,
    orig_shape,
    pose_conf_thresh,
    pose_kp_thresh,
    preprocess_mode="stretch",
):
    deq = {}
    for name, data in outputs.items():
        arr = np.array(data)
        if arr.ndim >= 1 and arr.shape[0] == 1:
            arr = arr[0]
        q = quant_info[name]
        deq[name] = dequantize(arr, q["scale"], q["zp"])

    mapped = map_outputs_by_shape(deq)

    boxes_80, scores_80, kpts_80 = decode_single_scale(mapped["80_box"], mapped["80_cls"], mapped["80_kpt"], stride=8)
    boxes_40, scores_40, kpts_40 = decode_single_scale(mapped["40_box"], mapped["40_cls"], mapped["40_kpt"], stride=16)
    boxes_20, scores_20, kpts_20 = decode_single_scale(mapped["20_box"], mapped["20_cls"], mapped["20_kpt"], stride=32)

    boxes = np.concatenate([boxes_80, boxes_40, boxes_20], axis=0)
    scores = np.concatenate([scores_80, scores_40, scores_20], axis=0)
    keypoints = np.concatenate([kpts_80, kpts_40, kpts_20], axis=0)

    keep_mask = scores > pose_conf_thresh
    boxes = boxes[keep_mask]
    scores = scores[keep_mask]
    keypoints = keypoints[keep_mask]

    if len(boxes) == 0:
        return {}, np.zeros((0, 4), dtype=np.float32), np.zeros((0,), dtype=np.float32), np.zeros((0, NUM_KEYPOINTS, 3), dtype=np.float32)

    keep = nms_pose(boxes, scores, iou_thresh=POSE_NMS_IOU_THRESH, max_det=POSE_MAX_DETECTIONS)
    boxes = boxes[keep]
    scores = scores[keep]
    keypoints = keypoints[keep]

    orig_h, orig_w = orig_shape
    if preprocess_mode == "letterbox":
        scale = min(POSE_INPUT_W / orig_w, POSE_INPUT_H / orig_h)
        resized_w = int(round(orig_w * scale))
        resized_h = int(round(orig_h * scale))
        pad_x = (POSE_INPUT_W - resized_w) // 2
        pad_y = (POSE_INPUT_H - resized_h) // 2
        boxes, keypoints = scale_coords_back_letterbox(boxes, keypoints, scale, pad_x, pad_y, orig_w, orig_h)
    else:
        sx = orig_w / float(POSE_INPUT_W)
        sy = orig_h / float(POSE_INPUT_H)
        boxes, keypoints = scale_coords_back_stretch(boxes, keypoints, sx, sy, orig_w, orig_h)

    result = {}
    if len(keypoints) > 0:
        for i, kp in enumerate(keypoints[0]):
            kx, ky, ks = kp
            inside_image_margin = (
                -0.02 * orig_w <= kx <= 1.02 * orig_w and
                -0.02 * orig_h <= ky <= 1.02 * orig_h
            )
            if ks >= pose_kp_thresh and inside_image_margin:
                result[int(i)] = (float(kx), float(ky), float(ks))

    return result, boxes, scores, keypoints


def extract_jersey_feature(image: np.ndarray, xyxy: np.ndarray) -> Optional[np.ndarray]:
    h_img, w_img = image.shape[:2]
    x1, y1, x2, y2 = xyxy.astype(np.int32)

    x1 = int(np.clip(x1, 0, w_img - 1))
    x2 = int(np.clip(x2, 0, w_img - 1))
    y1 = int(np.clip(y1, 0, h_img - 1))
    y2 = int(np.clip(y2, 0, h_img - 1))

    if x2 <= x1 or y2 <= y1:
        return None

    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    upper = crop[:max(1, int(0.55 * crop.shape[0])), :]
    if upper.size == 0:
        return None

    hsv = cv2.cvtColor(upper, cv2.COLOR_BGR2HSV)
    green = cv2.inRange(
        hsv,
        np.array([25, 35, 25], dtype=np.uint8),
        np.array([95, 255, 255], dtype=np.uint8)
    )
    mask = green == 0
    pixels = upper[mask]

    if len(pixels) < 30:
        pixels = upper.reshape(-1, 3)

    if len(pixels) == 0:
        return None

    lab = cv2.cvtColor(pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    return np.median(lab, axis=0).astype(np.float32)


def anchors_bottom_center(dets: np.ndarray) -> np.ndarray:
    if len(dets) == 0:
        return np.zeros((0, 2), dtype=np.float32)
    return np.stack([
        (dets[:, 0] + dets[:, 2]) * 0.5,
        dets[:, 3],
    ], axis=1).astype(np.float32)


def assign_teams(image: np.ndarray, dets: np.ndarray) -> np.ndarray:
    team_ids = np.full((len(dets),), -1, dtype=np.int32)
    if len(dets) == 0:
        return team_ids

    classes = dets[:, 5].astype(np.int32)
    player_idx = np.where(classes == PLAYER_CLASS_ID)[0]

    features = []
    feat_det_idx = []
    for i in player_idx:
        feat = extract_jersey_feature(image, dets[i, :4])
        if feat is not None:
            features.append(feat)
            feat_det_idx.append(i)

    if len(features) >= 2:
        Z = np.array(features, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
        _, labels, _ = cv2.kmeans(Z, 2, None, criteria, 8, cv2.KMEANS_PP_CENTERS)
        labels = labels.reshape(-1).astype(np.int32)
        for i, lab in zip(feat_det_idx, labels):
            team_ids[i] = int(lab)
    elif len(player_idx) == 1:
        team_ids[player_idx[0]] = 0

    for i in player_idx:
        if team_ids[i] < 0:
            team_ids[i] = 0

    gk_idx = np.where(classes == GOALKEEPER_CLASS_ID)[0]
    if len(gk_idx) > 0 and len(player_idx) > 0:
        player_xy = anchors_bottom_center(dets[player_idx])
        t0_mask = team_ids[player_idx] == 0
        t1_mask = team_ids[player_idx] == 1

        c0 = np.mean(player_xy[t0_mask], axis=0) if np.any(t0_mask) else np.mean(player_xy, axis=0)
        c1 = np.mean(player_xy[t1_mask], axis=0) if np.any(t1_mask) else np.mean(player_xy, axis=0)

        gk_xy = anchors_bottom_center(dets[gk_idx])
        for i, p in zip(gk_idx, gk_xy):
            d0 = float(np.linalg.norm(p - c0))
            d1 = float(np.linalg.norm(p - c1))
            team_ids[i] = 0 if d0 <= d1 else 1

    return team_ids


class TeamColorStabilizer:
    def __init__(self, alpha: float = 0.08, min_features: int = 4, max_distance: float = 45.0):
        self.alpha = float(alpha)
        self.min_features = int(min_features)
        self.max_distance = float(max_distance)
        self.centers: Optional[np.ndarray] = None

    def assign(self, image: np.ndarray, dets: np.ndarray) -> np.ndarray:
        team_ids = np.full((len(dets),), -1, dtype=np.int32)
        if len(dets) == 0:
            return team_ids

        classes = dets[:, 5].astype(np.int32)
        player_idx = np.where(classes == PLAYER_CLASS_ID)[0]

        features = []
        feat_det_idx = []
        for i in player_idx:
            feat = extract_jersey_feature(image, dets[i, :4])
            if feat is not None:
                features.append(feat)
                feat_det_idx.append(i)

        if len(features) >= 2:
            Z = np.array(features, dtype=np.float32)
            if self.centers is None and len(features) >= self.min_features:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
                _, labels, centers = cv2.kmeans(Z, 2, None, criteria, 8, cv2.KMEANS_PP_CENTERS)
                centers = centers.astype(np.float32)
                order = np.argsort(centers[:, 0])
                centers = centers[order]
                inv = np.zeros((2,), dtype=np.int32)
                inv[order] = np.arange(2, dtype=np.int32)
                labels = inv[labels.reshape(-1).astype(np.int32)]
                self.centers = centers
            elif self.centers is not None:
                dists = np.linalg.norm(Z[:, None, :] - self.centers[None, :, :], axis=2)
                labels = np.argmin(dists, axis=1).astype(np.int32)
                min_dists = np.min(dists, axis=1)
                for team in (0, 1):
                    mask = labels == team
                    if np.any(mask):
                        reliable = mask & (min_dists <= self.max_distance)
                        if np.any(reliable):
                            obs = np.median(Z[reliable], axis=0).astype(np.float32)
                            self.centers[team] = (1.0 - self.alpha) * self.centers[team] + self.alpha * obs
            else:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
                _, labels, _ = cv2.kmeans(Z, 2, None, criteria, 8, cv2.KMEANS_PP_CENTERS)
                labels = labels.reshape(-1).astype(np.int32)

            for i, lab in zip(feat_det_idx, labels):
                team_ids[i] = int(lab)
        elif len(player_idx) == 1:
            team_ids[player_idx[0]] = 0

        for i in player_idx:
            if team_ids[i] < 0:
                team_ids[i] = 0

        self._assign_goalkeepers(dets, team_ids, classes, player_idx)
        return team_ids

    @staticmethod
    def _assign_goalkeepers(dets: np.ndarray, team_ids: np.ndarray, classes: np.ndarray, player_idx: np.ndarray) -> None:
        gk_idx = np.where(classes == GOALKEEPER_CLASS_ID)[0]
        if len(gk_idx) == 0 or len(player_idx) == 0:
            return

        player_xy = anchors_bottom_center(dets[player_idx])
        t0_mask = team_ids[player_idx] == 0
        t1_mask = team_ids[player_idx] == 1
        c0 = np.mean(player_xy[t0_mask], axis=0) if np.any(t0_mask) else np.mean(player_xy, axis=0)
        c1 = np.mean(player_xy[t1_mask], axis=0) if np.any(t1_mask) else np.mean(player_xy, axis=0)

        gk_xy = anchors_bottom_center(dets[gk_idx])
        for i, p in zip(gk_idx, gk_xy):
            d0 = float(np.linalg.norm(p - c0))
            d1 = float(np.linalg.norm(p - c1))
            team_ids[i] = 0 if d0 <= d1 else 1


def pad_ball_boxes(dets: np.ndarray, px: float, width: int, height: int) -> np.ndarray:
    if len(dets) == 0 or px <= 0:
        return dets
    out = dets.copy()
    mask = out[:, 5].astype(np.int32) == BALL_CLASS_ID
    out[mask, 0] = np.clip(out[mask, 0] - px, 0, width - 1)
    out[mask, 1] = np.clip(out[mask, 1] - px, 0, height - 1)
    out[mask, 2] = np.clip(out[mask, 2] + px, 0, width - 1)
    out[mask, 3] = np.clip(out[mask, 3] + px, 0, height - 1)
    return out


def refine_ball_player_conflicts(
    dets: np.ndarray,
    width: int,
    height: int,
    max_height_ratio: float = 0.04,
    max_area_ratio: float = 0.0015,
    square_min: float = 0.55,
    square_max: float = 1.8,
    suppress_iou: float = 0.15,
) -> np.ndarray:
    if len(dets) == 0:
        return dets

    out = dets.copy()
    classes = out[:, 5].astype(np.int32)
    box_w = np.maximum(1.0, out[:, 2] - out[:, 0])
    box_h = np.maximum(1.0, out[:, 3] - out[:, 1])
    area = box_w * box_h
    aspect = box_w / box_h

    image_area = max(1.0, float(width * height))
    ball_like = (
        (classes != BALL_CLASS_ID)
        & (classes != GOALKEEPER_CLASS_ID)
        & (box_h <= float(height) * max_height_ratio)
        & (area <= image_area * max_area_ratio)
        & (aspect >= square_min)
        & (aspect <= square_max)
    )

    ball_idx = np.where(classes == BALL_CLASS_ID)[0]
    ball_like_idx = np.where(ball_like)[0]
    if len(ball_like_idx) == 0:
        return out

    if len(ball_idx) > 0:
        keep = np.ones((len(out),), dtype=bool)
        for i in ball_like_idx:
            cx = float((out[i, 0] + out[i, 2]) * 0.5)
            cy = float((out[i, 1] + out[i, 3]) * 0.5)
            for b in ball_idx:
                center_inside = out[b, 0] <= cx <= out[b, 2] and out[b, 1] <= cy <= out[b, 3]
                overlap = iou_xyxy(out[i, :4], out[b, :4]) >= suppress_iou
                if center_inside or overlap:
                    keep[i] = False
                    break
        return out[keep]

    # If the detector only produced a tiny square "player/referee", keep the strongest one as ball.
    best = int(ball_like_idx[np.argmax(out[ball_like_idx, 4])])
    out[best, 5] = float(BALL_CLASS_ID)
    return out


def open_socket(host: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def send_packet(sock: socket.socket, payload: Dict):
    data = (json.dumps(payload, separators=(',', ':')) + '\n').encode('utf-8')
    sock.sendall(data)


def draw_players(frame, players):
    out = frame.copy()

    for p in players:
        x1, y1, x2, y2, score, cls_id = p
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cls_id = int(cls_id)

        color = (255, 255, 255)
        if cls_id == BALL_CLASS_ID:
            color = (0, 0, 255)
        elif cls_id == GOALKEEPER_CLASS_ID:
            color = (0, 255, 255)
        elif cls_id == PLAYER_CLASS_ID:
            color = (0, 255, 0)
        elif cls_id == REFEREE_CLASS_ID:
            color = (255, 0, 0)

        label = CLASS_NAMES[cls_id] if 0 <= cls_id < len(CLASS_NAMES) else str(cls_id)

        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            out,
            f"{label} {score:.2f}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA
        )

    return out


def draw_keypoints(frame, keypoints_conf):
    out = frame.copy()
    for idx, (x, y, conf) in keypoints_conf.items():
        x = int(round(x))
        y = int(round(y))
        cv2.circle(out, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(
            out,
            f"{idx}",
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 0),
            1,
            cv2.LINE_AA
        )
    return out


def build_payload(frame_id, image, players, team_ids, jersey_features, keypoints_conf, source_image):
    h, w = image.shape[:2]

    keypoints = []
    for k, (x, y, c) in keypoints_conf.items():
        keypoints.append({
            "id": int(k),
            "x": float(x),
            "y": float(y),
            "conf": float(c),
        })

    detections = []
    for i, row in enumerate(players):
        x1, y1, x2, y2, conf, cls_id = row
        team = int(team_ids[i]) if i < len(team_ids) else -1
        detections.append({
            "x1": float(x1),
            "y1": float(y1),
            "x2": float(x2),
            "y2": float(y2),
            "conf": float(conf),
            "cls": int(cls_id),
            "team": team,
        })

    return {
        "frame_id": int(frame_id),
        "timestamp": time.time(),
        "image": {
            "width": int(w),
            "height": int(h),
        },
        "keypoints": keypoints,
        "detections": detections,
        "image_shape": [int(h), int(w)],
        "players": [[float(v) for v in row] for row in players.tolist()],
        "jersey_features": jersey_features,
        "keypoints_conf": {
            str(k): [float(v[0]), float(v[1]), float(v[2])]
            for k, v in keypoints_conf.items()
        },
        "class_names": CLASS_NAMES,
        "source_image": source_image,
    }


def print_frame_debug(frame_id, players, team_ids, keypoints_conf, infer_time, payload_bytes):
    kp_ids = sorted(keypoints_conf.keys())
    kp_conf = [float(keypoints_conf[k][2]) for k in kp_ids]
    if kp_ids:
        xs = [float(keypoints_conf[k][0]) for k in kp_ids]
        ys = [float(keypoints_conf[k][1]) for k in kp_ids]
        kp_summary = (
            f"kpts={len(kp_ids)} ids={kp_ids} "
            f"x=[{min(xs):.1f},{max(xs):.1f}] y=[{min(ys):.1f},{max(ys):.1f}] "
            f"conf=[{min(kp_conf):.2f},{max(kp_conf):.2f}]"
        )
    else:
        kp_summary = "kpts=0"

    if len(players) > 0:
        classes = players[:, 5].astype(np.int32)
        class_counts = {
            name: int(np.sum(classes == idx))
            for idx, name in enumerate(CLASS_NAMES)
        }
        team_summary = f"teams={team_ids.tolist()}"
    else:
        class_counts = {name: 0 for name in CLASS_NAMES}
        team_summary = "teams=[]"

    print(
        f"[frame {frame_id}] {infer_time * 1000:.1f} ms "
        f"players={len(players)} classes={class_counts} {team_summary} "
        f"{kp_summary} payload={payload_bytes}B"
    )


class FpsCounter:
    def __init__(self):
        self.t0 = time.time()
        self.count = 0

    def tick(self):
        self.count += 1
        now = time.time()
        elapsed = max(now - self.t0, 1e-6)
        return self.count / elapsed


def run_inference_on_frame(
    img,
    frame_id,
    args,
    det_pipe,
    pose_pipe,
    det_in_info,
    pose_in_info,
    pose_quant_info,
    ng_det,
    ng_pose,
    ng_det_params,
    ng_pose_params,
    keypoint_stabilizer=None,
    team_stabilizer=None,
    last_keypoints_conf=None,
    run_pose=True,
):
    orig_h, orig_w = img.shape[:2]
    if args.global_resize:
        infer_img, frame_sx, frame_sy = resize_frame_for_inference(img, MODEL_INPUT_SIZE)
    else:
        infer_img = img
        frame_sx = 1.0
        frame_sy = 1.0
    infer_h, infer_w = infer_img.shape[:2]

    det_h = int(det_in_info.shape[0])
    det_w = int(det_in_info.shape[1])

    if args.det_preprocess == "letterbox":
        det_input, det_scale, det_pad_x, det_pad_y = letterbox(infer_img, (det_w, det_h))
        det_scale_info = ("letterbox", det_scale, det_pad_x, det_pad_y)
    else:
        det_input = cv2.resize(infer_img, (det_w, det_h), interpolation=cv2.INTER_LINEAR)
        det_scale_info = ("stretch", infer_w / float(det_w), infer_h / float(det_h), 0.0)
    det_rgb = cv2.cvtColor(det_input, cv2.COLOR_BGR2RGB)
    det_tensor = np.ascontiguousarray(det_rgb, dtype=np.uint8)[None, ...]

    pose_tensor = None
    if run_pose:
        if args.pose_preprocess == "letterbox":
            pose_input, _, _, _ = letterbox(infer_img, (POSE_INPUT_W, POSE_INPUT_H))
            pose_input = cv2.cvtColor(pose_input, cv2.COLOR_BGR2RGB)
            pose_input = np.ascontiguousarray(pose_input, dtype=np.uint8)
        else:
            pose_input = preprocess_stretch_uint8(
                infer_img,
                (POSE_INPUT_W, POSE_INPUT_H),
                bgr_to_rgb=True,
            )
        pose_tensor = pose_input[None, ...]

    t0 = time.time()

    with ng_det.activate(ng_det_params):
        det_outputs = det_pipe.infer({det_in_info.name: det_tensor})

    pose_outputs = None
    if run_pose:
        with ng_pose.activate(ng_pose_params):
            pose_outputs = pose_pipe.infer({pose_in_info.name: pose_tensor})

    infer_time = time.time() - t0

    dets = decode_detector(
        det_outputs,
        (det_w, det_h),
        (infer_w, infer_h),
        conf_th=args.conf_player,
        iou_th=args.iou,
        ball_conf_th=args.conf_ball,
        scale_info=det_scale_info,
    )

    if dets:
        players = np.array([
            [d['box'][0], d['box'][1], d['box'][2], d['box'][3], d['score'], d['class_id']]
            for d in dets
        ], dtype=np.float32)
    else:
        players = np.zeros((0, 6), dtype=np.float32)
    players = scale_dets_from_resized_frame(players, frame_sx, frame_sy, orig_w, orig_h)
    if not args.no_ball_player_fix:
        players = refine_ball_player_conflicts(
            players,
            orig_w,
            orig_h,
            max_height_ratio=args.ball_player_max_height_ratio,
            max_area_ratio=args.ball_player_max_area_ratio,
            square_min=args.ball_player_square_min,
            square_max=args.ball_player_square_max,
            suppress_iou=args.ball_player_suppress_iou,
        )
    players = pad_ball_boxes(players, args.ball_pad, orig_w, orig_h)

    if run_pose and pose_outputs is not None:
        keypoints_conf, _, _, _ = decode_pose_outputs(
            pose_outputs,
            pose_quant_info,
            (infer_h, infer_w),
            args.pose_conf,
            args.pose_kp_th,
            preprocess_mode=args.pose_preprocess,
        )
        keypoints_conf = {
            k: (float(v[0] * frame_sx), float(v[1] * frame_sy), float(v[2]))
            for k, v in keypoints_conf.items()
        }

        if args.remap_kpts:
            keypoints_conf = remap_keypoints_to_semantic_with_conf(keypoints_conf)

        if keypoint_stabilizer is not None:
            keypoints_conf = keypoint_stabilizer.update(keypoints_conf)
    else:
        if keypoint_stabilizer is not None:
            keypoints_conf = keypoint_stabilizer.update({})
        else:
            keypoints_conf = last_keypoints_conf or {}

    if team_stabilizer is not None:
        team_ids = team_stabilizer.assign(img, players)
    else:
        team_ids = assign_teams(img, players)

    jersey_features = {}
    for idx, row in enumerate(players):
        cls_id = int(row[5])
        if cls_id in (PLAYER_CLASS_ID, GOALKEEPER_CLASS_ID):
            feat = extract_jersey_feature(img, row[:4])
            if feat is not None:
                jersey_features[str(idx)] = [float(feat[0]), float(feat[1]), float(feat[2])]

    payload = build_payload(
        frame_id=frame_id,
        image=img,
        players=players,
        team_ids=team_ids,
        jersey_features=jersey_features,
        keypoints_conf=keypoints_conf,
        source_image="rpicam" if args.rpicam else (args.camera or args.video or args.image),
    )

    return payload, players, team_ids, keypoints_conf, infer_time


def parse_camera_source(source: str):
    try:
        return int(source)
    except ValueError:
        return source


def camera_backend(name: str):
    name = (name or "auto").lower()
    if name == "v4l2":
        return cv2.CAP_V4L2
    if name == "gstreamer":
        return cv2.CAP_GSTREAMER
    if name == "any":
        return cv2.CAP_ANY
    return None


def build_rpicam_command(args) -> List[str]:
    cmd = [
        args.rpicam_cmd,
        "--codec", "mjpeg",
        "--timeout", "0",
        "--output", "-",
        "--nopreview",
    ]
    if args.camera_width > 0:
        cmd.extend(["--width", str(args.camera_width)])
    if args.camera_height > 0:
        cmd.extend(["--height", str(args.camera_height)])
    if args.camera_fps > 0:
        cmd.extend(["--framerate", str(args.camera_fps)])
    return cmd


def iter_rpicam_frames(args):
    cmd = build_rpicam_command(args)
    print("[INFO] rpicam:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if proc.stdout is None:
        raise RuntimeError("Impossible de lire stdout de rpicam-vid")

    buffer = bytearray()
    raw_id = 0
    sent_id = 0

    try:
        while True:
            chunk = proc.stdout.read(8192)
            if not chunk:
                if proc.poll() is not None:
                    raise RuntimeError(f"rpicam termine avec code {proc.returncode}")
                time.sleep(0.001)
                continue

            buffer.extend(chunk)
            while True:
                start = buffer.find(b"\xff\xd8")
                end = buffer.find(b"\xff\xd9", start + 2 if start >= 0 else 0)
                if start < 0 or end < 0:
                    if len(buffer) > 4_000_000:
                        del buffer[:-2]
                    break

                jpg = bytes(buffer[start:end + 2])
                del buffer[:end + 2]

                arr = np.frombuffer(jpg, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                if raw_id % max(1, args.stride) == 0:
                    yield sent_id, frame
                    sent_id += 1
                    if args.max_frames > 0 and sent_id >= args.max_frames:
                        return
                raw_id += 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()


def iter_frames(args):
    if args.video:
        if not os.path.isfile(args.video):
            raise FileNotFoundError(f'video introuvable: {args.video}')
        cap = cv2.VideoCapture(args.video)
        if not cap.isOpened():
            raise RuntimeError(f"Impossible d'ouvrir la video: {args.video}")

        raw_id = 0
        sent_id = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if raw_id % max(1, args.stride) == 0:
                yield sent_id, frame
                sent_id += 1
                if args.max_frames > 0 and sent_id >= args.max_frames:
                    break
            raw_id += 1
        cap.release()
        return

    if args.camera:
        source = parse_camera_source(args.camera)
        backend = camera_backend(args.camera_backend)
        cap = cv2.VideoCapture(source) if backend is None else cv2.VideoCapture(source, backend)
        if not cap.isOpened():
            raise RuntimeError(f"Impossible d'ouvrir la camera: {args.camera}")

        if args.camera_width > 0:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.camera_width)
        if args.camera_height > 0:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.camera_height)
        if args.camera_fps > 0:
            cap.set(cv2.CAP_PROP_FPS, args.camera_fps)

        raw_id = 0
        sent_id = 0
        failed_reads = 0
        while True:
            ok, frame = cap.read()
            if not ok or frame is None or frame.size == 0:
                failed_reads += 1
                if failed_reads % 30 == 1:
                    print("[WARN] Frame camera non lue, nouvelle tentative...")
                if failed_reads >= args.camera_max_failed_reads:
                    cap.release()
                    raise RuntimeError(
                        "Camera ouverte mais aucune frame recue. "
                        "Essaie --camera /dev/video0 --camera-backend v4l2, "
                        "ou verifie la camera avec: libcamera-hello / rpicam-hello / v4l2-ctl."
                    )
                time.sleep(0.01)
                continue
            failed_reads = 0
            if raw_id % max(1, args.stride) == 0:
                yield sent_id, frame
                sent_id += 1
                if args.max_frames > 0 and sent_id >= args.max_frames:
                    break
            raw_id += 1
        cap.release()
        return

    if args.rpicam:
        yield from iter_rpicam_frames(args)
        return

    if not os.path.isfile(args.image):
        raise FileNotFoundError(f'image introuvable: {args.image}')
    frame_bgr = cv2.imread(args.image)
    if frame_bgr is None:
        raise RuntimeError(f"Impossible de lire l'image: {args.image}")

    frame_id = 0
    while True:
        yield frame_id, frame_bgr.copy()
        frame_id += 1
        if not args.loop:
            break


def main():
    ap = argparse.ArgumentParser(description="Sender image/video test with Hailo inference and TCP sending")
    ap.add_argument('--host', default='10.145.103.196')
    ap.add_argument('--port', type=int, default=5000)
    ap.add_argument('--players-hef', default='players_h8l.hef')
    ap.add_argument('--key-hef', default='yolov8s_pose.hef')
    ap.add_argument('--image', default='match_frame.jpg')
    ap.add_argument('--video', default='', help='chemin video, ex: match.mp4')
    ap.add_argument('--rpicam', dest='rpicam', action='store_true', default=True, help='utiliser rpicam-vid/libcamera comme source camera Raspberry Pi')
    ap.add_argument('--no-rpicam', dest='rpicam', action='store_false', help='desactiver rpicam et utiliser --video/--camera/--image')
    ap.add_argument('--rpicam-cmd', default='rpicam-vid', help='commande rpicam, ex: rpicam-vid ou libcamera-vid')
    ap.add_argument('--camera', default='', help='source camera OpenCV, ex: 0 ou /dev/video0 ou rtsp://...')
    ap.add_argument('--camera-width', type=int, default=1280, help='largeur camera demandee, 0 = defaut camera')
    ap.add_argument('--camera-height', type=int, default=720, help='hauteur camera demandee, 0 = defaut camera')
    ap.add_argument('--camera-fps', type=int, default=30, help='FPS camera demande, 0 = defaut camera')
    ap.add_argument('--camera-backend', choices=['auto', 'any', 'v4l2', 'gstreamer'], default='auto', help='backend OpenCV pour la camera')
    ap.add_argument('--camera-max-failed-reads', type=int, default=120, help='nombre max de lectures camera echouees avant erreur')
    ap.add_argument('--stride', type=int, default=1, help='envoyer une frame sur N pour video/camera')
    ap.add_argument('--max-frames', type=int, default=0, help='limite de frames envoyees, 0 = tout')
    ap.add_argument('--pose-every', type=int, default=3, help='calculer les keypoints terrain toutes les N frames pour gagner en FPS')
    ap.add_argument('--log-every', type=int, default=30, help='afficher les logs toutes les N frames')
    ap.add_argument('--global-resize', action='store_true', help='ancien mode: redimensionner toute la frame en 640x640 avant les deux modeles')
    ap.add_argument('--conf-player', type=float, default=DET_CONF_TH)
    ap.add_argument('--conf-ball', type=float, default=0.05)
    ap.add_argument('--ball-pad', type=float, default=12.0, help='padding pixels autour de la box balle, comme le notebook')
    ap.add_argument('--no-ball-player-fix', action='store_true', help='desactiver la correction des petites boxes player/referee qui sont probablement la balle')
    ap.add_argument('--ball-player-max-height-ratio', type=float, default=0.04, help='hauteur max relative pour reclasser une petite box comme balle')
    ap.add_argument('--ball-player-max-area-ratio', type=float, default=0.0015, help='surface max relative pour reclasser une petite box comme balle')
    ap.add_argument('--ball-player-square-min', type=float, default=0.55, help='aspect ratio min pour une box candidate balle')
    ap.add_argument('--ball-player-square-max', type=float, default=1.8, help='aspect ratio max pour une box candidate balle')
    ap.add_argument('--ball-player-suppress-iou', type=float, default=0.15, help='IoU min pour supprimer une petite fausse box joueur autour de la balle')
    ap.add_argument('--iou', type=float, default=DET_IOU_TH)
    ap.add_argument('--pose-conf', type=float, default=POSE_CONF_THRESH)
    ap.add_argument('--pose-kp-th', type=float, default=POSE_KP_THRESH)
    ap.add_argument('--kpt-smooth-alpha', type=float, default=KPT_SMOOTH_ALPHA, help='EMA alpha pour lisser les keypoints terrain avant envoi')
    ap.add_argument('--kpt-max-jump', type=float, default=KPT_MAX_JUMP, help='rejeter un keypoint s il saute de plus de N pixels')
    ap.add_argument('--kpt-hold-frames', type=int, default=KPT_HOLD_FRAMES, help='garder les derniers keypoints valides pendant N frames')
    ap.add_argument('--no-kpt-stabilizer', action='store_true', help='desactiver le stabilisateur temporel des keypoints')
    ap.add_argument('--team-alpha', type=float, default=0.08, help='EMA alpha pour stabiliser les centres couleur des equipes')
    ap.add_argument('--team-max-distance', type=float, default=45.0, help='distance LAB max pour mettre a jour un centre equipe')
    ap.add_argument('--no-team-stabilizer', action='store_true', help='desactiver la stabilisation temporelle des equipes')
    ap.add_argument('--det-preprocess', choices=['letterbox', 'stretch'], default='letterbox')
    ap.add_argument('--pose-preprocess', choices=['stretch', 'letterbox'], default='stretch')
    ap.add_argument('--remap-kpts', action='store_true', help='remapper les indices de keypoints avec KEYPOINT_CLASS_TO_LABEL')
    ap.add_argument('--save-payload', default='', help='sauvegarder le dernier JSON envoye')
    ap.add_argument('--save-debug', default='', help='sauvegarder image debug sender')
    ap.add_argument('--no-preview', dest='no_preview', action='store_true', default=True, help='ne pas afficher la fenetre OpenCV cote sender')
    ap.add_argument('--preview', dest='no_preview', action='store_false', help='afficher la fenetre OpenCV cote sender')
    ap.add_argument('--loop', action='store_true', help='renvoyer la meme image en boucle')
    args = ap.parse_args()

    if not os.path.isfile(args.players_hef):
        raise FileNotFoundError(f'players hef introuvable: {args.players_hef}')
    if not os.path.isfile(args.key_hef):
        raise FileNotFoundError(f'key hef introuvable: {args.key_hef}')

    sock = open_socket(args.host, args.port)

    hef_det = hp.HEF(args.players_hef)
    hef_pose = hp.HEF(args.key_hef)

    det_in_info = hef_det.get_input_vstream_infos()[0]
    pose_in_info = hef_pose.get_input_vstream_infos()[0]
    pose_output_infos = hef_pose.get_output_vstream_infos()

    pose_quant_info = {
        info.name: {
            'scale': info.quant_info.qp_scale,
            'zp': info.quant_info.qp_zp,
            'shape': tuple(info.shape),
        }
        for info in pose_output_infos
    }

    params = hp.VDevice.create_params()
    if hasattr(params, 'scheduling_algorithm') and hasattr(hp, 'HailoSchedulingAlgorithm'):
        params.scheduling_algorithm = hp.HailoSchedulingAlgorithm.NONE

    with hp.VDevice(params=params) as dev:
        det_cfg = hp.ConfigureParams.create_from_hef(
            hef_det,
            interface=hp.HailoStreamInterface.PCIe
        )
        pose_cfg = hp.ConfigureParams.create_from_hef(
            hef_pose,
            interface=hp.HailoStreamInterface.PCIe
        )

        ng_det = dev.configure(hef_det, det_cfg)[0]
        ng_pose = dev.configure(hef_pose, pose_cfg)[0]

        ng_det_params = ng_det.create_params()
        ng_pose_params = ng_pose.create_params()

        det_in_p = hp.InputVStreamParams.make(
            ng_det,
            quantized=True,
            format_type=hp.FormatType.UINT8
        )
        det_out_p = hp.OutputVStreamParams.make(
            ng_det,
            quantized=False,
            format_type=hp.FormatType.FLOAT32
        )

        pose_in_p = hp.InputVStreamParams.make(
            ng_pose,
            quantized=True,
            format_type=hp.FormatType.UINT8
        )
        pose_out_p = hp.OutputVStreamParams.make(
            ng_pose,
            quantized=True,
            format_type=hp.FormatType.AUTO
        )

        with hp.InferVStreams(ng_det, det_in_p, det_out_p) as det_pipe, \
             hp.InferVStreams(ng_pose, pose_in_p, pose_out_p) as pose_pipe:

            last_keypoints_conf = {}
            keypoint_stabilizer = None
            if not args.no_kpt_stabilizer:
                keypoint_stabilizer = KeypointStabilizer(
                    alpha=args.kpt_smooth_alpha,
                    max_jump=args.kpt_max_jump,
                    hold_frames=args.kpt_hold_frames,
                )
            team_stabilizer = None
            if not args.no_team_stabilizer:
                team_stabilizer = TeamColorStabilizer(
                    alpha=args.team_alpha,
                    max_distance=args.team_max_distance,
                )
            fps_counter = FpsCounter()
            for frame_id, img in iter_frames(args):
                run_pose = frame_id == 0 or frame_id % max(1, args.pose_every) == 0 or not last_keypoints_conf
                payload, players, team_ids, keypoints_conf, infer_time = run_inference_on_frame(
                    img=img,
                    frame_id=frame_id,
                    args=args,
                    det_pipe=det_pipe,
                    pose_pipe=pose_pipe,
                    det_in_info=det_in_info,
                    pose_in_info=pose_in_info,
                    pose_quant_info=pose_quant_info,
                    ng_det=ng_det,
                    ng_pose=ng_pose,
                    ng_det_params=ng_det_params,
                    ng_pose_params=ng_pose_params,
                    keypoint_stabilizer=keypoint_stabilizer,
                    team_stabilizer=team_stabilizer,
                    last_keypoints_conf=last_keypoints_conf,
                    run_pose=run_pose,
                )
                if keypoints_conf:
                    last_keypoints_conf = keypoints_conf

                send_packet(sock, payload)
                payload_bytes = len(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
                fps = fps_counter.tick()
                if args.log_every > 0 and frame_id % args.log_every == 0:
                    print_frame_debug(frame_id, players, team_ids, keypoints_conf, infer_time, payload_bytes)
                    print(f"[fps] avg={fps:.1f} pose={'yes' if run_pose else 'reuse'}")

                vis = draw_players(img, players)
                vis = draw_keypoints(vis, keypoints_conf)

                cv2.putText(
                    vis,
                    f"Frame {frame_id} | Players: {len(players)} | Pitch pts: {len(keypoints_conf)} | {infer_time*1000:.1f} ms",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                if not args.no_preview:
                    cv2.imshow("Sender Image/Video Test", vis)
                if args.save_debug:
                    cv2.imwrite(args.save_debug, vis)
                if args.save_payload:
                    with open(args.save_payload, "w", encoding="utf-8") as f:
                        json.dump(payload, f, ensure_ascii=True, indent=2)
                key = cv2.waitKey(1 if args.video or args.camera or args.rpicam or args.loop else 0) & 0xFF if not args.no_preview else 255

                if key == ord('q'):
                    break

    sock.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
