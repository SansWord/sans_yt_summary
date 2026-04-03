# Shia LaBeouf "Just Do It" Motivational Speech (Original Video by LaBeouf, Rönkkö & Turner)
https://www.youtube.com/watch?v=ZXsQAXx_ao0

## Timestamp Summary

- [[0:02]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=2) System requirements: "Don't let your dreams be dreams" — problem statement
- [[0:08]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=8) Root cause identified: "Yesterday you said tomorrow" — circular dependency detected
- [[0:15]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=15) Solution deployed: "Just do it!" — core API call
- [[0:25]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=25) Performance note: wake up and work hard, don't rely on dream cache
- [[0:45]](https://www.youtube.com/watch?v=ZXsQAXx_ao0&t=45) SLA declaration: "Nothing is impossible"

---

## High-Level Design (ASCII)

```
┌──────────────────────────────────────────────────────┐
│                     USER (You)                       │
└─────────────────────────┬────────────────────────────┘
                          │ has a dream
                          ▼
┌──────────────────────────────────────────────────────┐
│                  Dream Queue Service                 │
│  [do it tomorrow] ──X──  [do it tomorrow] ──X──      │
│                    ↓ (Shia intervenes)               │
│                 Action Dispatcher                    │
└─────────────────────────┬────────────────────────────┘
                          │ Just Do It
                          ▼
┌──────────────────────────────────────────────────────┐
│                   Results Database                   │
│              Dream fulfillment rate: 100%            │
└──────────────────────────────────────────────────────┘
```

---

## DB Schema

```sql
CREATE TABLE dreams (
  id             UUID PRIMARY KEY,
  content        TEXT NOT NULL,
  status         ENUM('pending', 'said_tomorrow', 'just_did_it'),
  created_at     TIMESTAMP,
  tomorrow_count INT DEFAULT 0  -- dangerous column, needs a cap
);

CREATE TABLE actions (
  id          UUID PRIMARY KEY,
  dream_id    UUID REFERENCES dreams(id),
  executed_at TIMESTAMP NOT NULL,
  impossible  BOOLEAN DEFAULT FALSE  -- per the SLA, always FALSE
);
```

---

## Critical Design Decisions

| Decision | Rationale |
|----------|-----------|
| Remove tomorrow cache | "Yesterday you said tomorrow" — set TTL to 0 |
| Make action queue synchronous | Async dreams never ship; execute immediately |
| Drop the impossible flag | Per SLA: nothing is impossible |

---

## Main Challenges

The core bottleneck is not technical — it is **human procrastination causing write amplification**. Each "tomorrow" schedules a new job that never executes, eventually causing queue overflow.

---

## Engineering Level Assessment

**Staff Level — unambiguously**

Shia completed requirements analysis, bottleneck identification, solution design, deployment, and SLA commitment in 55 seconds.

| Level | Expected knowledge for this problem |
|-------|-------------------------------------|
| Junior | Knows what a queue is |
| Mid | Knows queues can overflow |
| Senior | Knows how to drain the queue |
| Staff | Eliminates the queue entirely. Just Do It. |

---

## High-Level Design Review (Senior/Staff Standard)

The original design lacks a **retry mechanism** and **dead letter queue** for genuinely hard dreams. Improved version:

```
Dreams → Validator → Action Dispatcher
                          ↓ failure
                     Retry (max 3 attempts)
                          ↓ still failing
                     "Nothing is Impossible" Handler
                          ↓
                     Force execute
```

**Conclusion:** This is not a system design video. But if life were a distributed system, Shia LaBeouf just solved the consistency problem.
