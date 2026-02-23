"""
Sample code snippets for the Smart Code Reviewer demo.
"""

SAMPLES: dict[str, dict[str, str]] = {
    "Python – Clean Example": {
        "language": "python",
        "code": '''\
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Immutable value object representing a monetary amount."""

    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Amount must be non-negative, got {self.amount}")

    def add(self, other: Money) -> Money:
        """Return a new Money instance with the sum of both amounts."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add {self.currency} and {other.currency}"
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def display(self) -> str:
        """Human-friendly representation."""
        return f"{self.currency} {self.amount:,.2f}"
''',
    },
    "Python – Needs Improvement": {
        "language": "python",
        "code": '''\
import os, sys, json, re
from datetime import *

def proc(d):
    r = []
    for i in range(len(d)):
        x = d[i]
        if x["type"] == "A":
            v = x["val"] * 1.1
        elif x["type"] == "B":
            v = x["val"] * 0.9
        elif x["type"] == "C":
            v = x["val"] * 1.05
        else:
            v = x["val"]
        x["result"] = v
        x["ts"] = datetime.now().isoformat()
        r.append(x)
    return r

def save(d, fn):
    f = open(fn, "w")
    f.write(json.dumps(d))
    f.close()

data = [{"type":"A","val":100},{"type":"B","val":200},{"type":"C","val":300},{"type":"D","val":400}]
result = proc(data)
save(result, "out.json")
print("done")
''',
    },
    "JavaScript – API Handler": {
        "language": "javascript",
        "code": '''\
const express = require('express');
const router = express.Router();

router.get('/users', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    const users = await db.query(
      'SELECT id, name, email FROM users LIMIT ? OFFSET ?',
      [limit, offset]
    );

    const [{ total }] = await db.query('SELECT COUNT(*) as total FROM users');

    res.json({
      data: users,
      pagination: { page, limit, total, pages: Math.ceil(total / limit) },
    });
  } catch (err) {
    console.error('Failed to fetch users:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/users', async (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'name and email required' });
  try {
    const result = await db.query('INSERT INTO users (name, email) VALUES (?, ?)', [name, email]);
    res.status(201).json({ id: result.insertId, name, email });
  } catch (err) {
    if (err.code === 'ER_DUP_ENTRY') return res.status(409).json({ error: 'Email already exists' });
    console.error('Failed to create user:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
''',
    },
    "Java – Singleton Pattern": {
        "language": "java",
        "code": '''\
public class ConfigManager {
    private static ConfigManager instance;
    private Map<String, String> config = new HashMap<>();
    private String filePath;

    private ConfigManager() {}

    public static ConfigManager getInstance() {
        if (instance == null) {
            instance = new ConfigManager();
        }
        return instance;
    }

    public void loadConfig(String path) {
        this.filePath = path;
        try {
            BufferedReader reader = new BufferedReader(new FileReader(path));
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=");
                if (parts.length == 2) {
                    config.put(parts[0].trim(), parts[1].trim());
                }
            }
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public String get(String key) {
        return config.get(key);
    }

    public void set(String key, String value) {
        config.put(key, value);
    }
}
''',
    },
}
