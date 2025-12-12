import express from "express";
import cors from "cors";
import { randomUUID } from "crypto";

const app = express();
app.use(cors());
app.use(express.json());

app.use(express.static('.'));

const idemStore = new Map(); 
const rate = new Map();     

const WINDOW_MS = 10_000;
const MAX_REQ = 5;

const now = () => Date.now();

// 1. Middleware: X-Request-Id (Кореляція)
app.use((req, res, next) => {
    const rid = req.get("X-Request-Id") || randomUUID();
    req.rid = rid;
    res.setHeader("X-Request-Id", rid);
    console.log(`[${new Date().toISOString()}] -> ${req.method} ${req.url} (RID: ${rid})`);
    next();
});

// 2. Middleware: Rate Limit + Retry-After
app.use((req, res, next) => {
    const ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress || "local";
    const b = rate.get(ip) ?? { count: 0, ts: now() };
    const within = now() - b.ts < WINDOW_MS;
    
    const state = within ? { count: b.count + 1, ts: b.ts } : { count: 1, ts: now() };
    rate.set(ip, state);

    if (state.count > MAX_REQ) {
        console.warn(`!!! Rate Limit Exceeded for ${ip}`);
        res.setHeader("Retry-After", "3");
        return res.status(429).json({ 
            error: "too_many_requests", 
            code: "RATE_LIMIT",
            requestId: req.rid 
        });
    }
    next();
});

// 3. Middleware: Chaos Engineering (Штучні збої)
app.use(async (_req, res, next) => {
    if (_req.path === '/health') return next();

    const r = Math.random();
    
    if (r < 0.15) {
        console.log("... injecting delay ...");
        await new Promise(resolve => setTimeout(resolve, 2000)); 
    }

    if (r > 0.80) {
        const errType = Math.random() < 0.5 ? "unavailable" : "unexpected";
        const code = errType === "unavailable" ? 503 : 500;
        console.error(`X Error Injected: ${code}`);
        return res.status(code).json({ 
            error: errType, 
            code: code === 503 ? "SERVICE_UNAVAILABLE" : "SERVER_ERROR",
            requestId: _req.rid 
        });
    }
    next();
});

// 4. POST /orders - Створити (Ідемпотентний)
app.post("/orders", (req, res) => {
    const key = req.get("Idempotency-Key");
    
    if (!key) {
        return res.status(400).json({ error: "idempotency_key_required", requestId: req.rid });
    }

    if (idemStore.has(key)) {
        console.log(`@ Idempotency Hit: ${key}`);
        return res.status(200).json({ 
            ...idemStore.get(key), 
            requestId: req.rid,
            status: "cached" 
        });
    }

    const order = { 
        id: "ord_" + randomUUID().slice(0, 8), 
        title: req.body?.title ?? "Untitled",
        createdAt: new Date().toISOString()
    };
    
    idemStore.set(key, order);
    console.log(`$ New Order Created: ${order.id}`);
    
    return res.status(201).json({ ...order, requestId: req.rid, status: "created" });
});

// 5. GET /orders - Отримати список
app.get("/orders", (req, res) => {
    const list = Array.from(idemStore.values());
    console.log(`? List Requested. Count: ${list.length}`);
    return res.json(list);
});

// 6. DELETE /orders/:id - Видалити
app.delete("/orders/:id", (req, res) => {
    const { id } = req.params;
    let found = false;

    for (const [key, value] of idemStore.entries()) {
        if (value.id === id) {
            idemStore.delete(key);
            found = true;
            break;
        }
    }

    if (found) {
        console.log(`- Deleted: ${id}`);
        return res.status(204).send();
    } else {
        console.warn(`! Delete failed. Not found: ${id}`);
        return res.status(404).json({ error: "not_found", requestId: req.rid });
    }
});

// 7. Health Check
app.get("/health", async (req, res) => {
    const delay = req.query.delay ? parseInt(req.query.delay) : 0;
    if (delay > 0) await new Promise(r => setTimeout(r, delay));
    res.json({ status: "ok" });
});

app.listen(8081, () => console.log("🚀 Server running on http://localhost:8081"));