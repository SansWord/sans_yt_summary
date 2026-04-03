# Shia LaBeouf "Just Do It" Motivational Speech (Original Video by LaBeouf, Rönkkö & Turner)
https://www.youtube.com/watch?v=ZXsQAXx_ao0

## 時間戳記摘要

- [[0:02]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=2) 系統初始化：「Don't let your dreams be dreams」— 需求確認
- [[0:08]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=8) 發現關鍵瓶頸：「Yesterday you said tomorrow」— 循環依賴問題
- [[0:15]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=15) 解決方案部署：「Just do it!」— 核心 API call
- [[0:25]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=25) 效能優化建議：醒來並努力工作，而非僅依賴 dream cache
- [[0:45]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=45) 系統保證：「Nothing is impossible」— SLA 聲明

---

## High Level Design (ASCII)

```
┌─────────────────────────────────────────────────────┐
│                   USER (你)                          │
└──────────────────────┬──────────────────────────────┘
                       │ 有夢想
                       ▼
┌─────────────────────────────────────────────────────┐
│              Dream Queue Service                     │
│  [明天再說] ──X──  [明天再說] ──X──  [明天再說]      │
│                   ↓ (Shia 介入)                      │
│              Action Dispatcher                       │
└──────────────────────┬──────────────────────────────┘
                       │ Just Do It
                       ▼
┌─────────────────────────────────────────────────────┐
│                  結果 (Results DB)                   │
│            夢想實現率: 100% (理論值)                  │
└─────────────────────────────────────────────────────┘
```

---

## DB Schema

```sql
CREATE TABLE dreams (
  id          UUID PRIMARY KEY,
  content     TEXT NOT NULL,
  status      ENUM('pending', 'said_tomorrow', 'just_did_it'),
  created_at  TIMESTAMP,
  tomorrow_count INT DEFAULT 0  -- 危險欄位，應設上限
);

CREATE TABLE actions (
  id          UUID PRIMARY KEY,
  dream_id    UUID REFERENCES dreams(id),
  executed_at TIMESTAMP NOT NULL,
  impossible  BOOLEAN DEFAULT FALSE  -- 根據影片，此欄位永遠為 FALSE
);
```

---

## Critical Design Decisions

| 決策 | 說明 |
|------|------|
| 移除 tomorrow cache | 昨天你說明天，明天你還是說明天 — TTL 設為 0 |
| Action Queue 改為同步 | 非同步夢想從未實現，改為立即執行 |
| 拒絕 impossible flag | 根據 SLA，不可能不存在 |

---

## 主要難點

此系統的核心難點不在技術，而在**人類拖延行為**造成的 write amplification：每次「明天」觸發一次新的 scheduled job，但 job 永遠不執行，最終 queue 爆滿。

---

## 職級判斷

**Staff Level（毫無疑問）**

Shia 在 55 秒內完成了：需求分析、瓶頸定位、解決方案設計、部署、SLA 保證。

| 職級 | 面試此題應具備的知識 |
|------|---------------------|
| Junior | 知道什麼是 queue |
| Mid | 知道 queue 會爆 |
| Senior | 知道要清 queue |
| Staff | 直接消滅 queue，Just Do It |

---

## High Level Design 改進建議（Senior/Staff 標準）

原版設計缺少 **retry mechanism** 與 **dead letter queue** 處理真正困難的夢想。改進版：

```
Dreams → Validator → Action Dispatcher
                          ↓ 失敗
                     Retry (最多3次)
                          ↓ 仍失敗
                     "Nothing is impossible" Handler
                          ↓
                     強制執行
```

**結論：** 這不是系統設計影片。但如果人生是一個分散式系統，Shia LaBeouf 剛剛解決了 consistency 問題。
