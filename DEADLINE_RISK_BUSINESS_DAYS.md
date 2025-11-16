# Deadline Risk - Business Days Calculation

## 📊 Ako to funguje

Backend systém teraz počíta **iba pracovné dni (Pondelok-Piatok)** pri kontrole deadline risks, čo je realistickejšie pre projekt management.

---

## 🔢 **Výpočet Business Days**

### **Algoritmus:**
```python
def _count_business_days(start_date, end_date):
    # 1. Vypočíta plné týždne (každý = 5 pracovných dní)
    # 2. Zvyšné dni počíta individuálne
    # 3. Vynecháva Sobotu (weekday=5) a Nedeľu (weekday=6)
```

### **Príklad:**
- **Pondelok → Piatok**: 5 pracovných dní
- **Pondelok → Nedeľa**: 5 pracovných dní (víkend sa neráta)
- **Sobota → Nedeľa**: 0 pracovných dní
- **10 kalendárnych dní**: ~7-8 pracovných dní (závisí od dňa v týždni)

---

## ⚠️ **Deadline Risk Detection**

### **Kedy sa vytvorí proposal:**

```python
buffer = business_days_remaining - estimated_days

if buffer < 3:  # Menej ako 3 pracovné dni rezervy
    if buffer < 1:
        severity = 'critical'  # Urgentné!
    else:
        severity = 'important'  # Treba riešiť
```

### **Konverzia PERT Estimates:**
- **PERT Expected** je v hodinách → konvertuje sa na dni: `hours / 8`
- **Story Points** fallback: `SP × 0.5 dní`

---

## 📅 **Realistický príklad:**

### **Scenario:**
- **Dnes:** Piatok 15:00
- **Deadline:** Nasledujúci Piatok 17:00
- **Kalendárne dni:** 7 dní
- **Pracovné dni:** **5 dní** (Pondelok-Piatok, vynecháva víkend)

### **Task s PERT Estimates:**
- Optimistic: 16h (2 dni)
- Most Likely: 24h (3 dni)  
- Pessimistic: 40h (5 dní)
- **Expected:** `(16 + 4×24 + 40) / 6 = 26h = 3.25 dní`

### **Buffer Calculation:**
```
business_days_remaining = 5 dní
estimated_days = 3.25 dní
buffer = 5 - 3.25 = 1.75 dní
```

**→ Buffer < 3 dní → IMPORTANT deadline risk! ⚠️**

---

## 🎯 **Output v Proposals:**

```json
{
  "type": "deadline_risk",
  "severity": "important",
  "title": "Deadline risk: 'Feature X' due in 5 working days",
  "description": "Task may miss deadline with only 1.8 working days buffer",
  "reason": "Task 'Feature X' needs 3.3 working days but deadline is in 5 working days (Mon-Fri). Buffer: 1.8 days.",
  "impact": {
    "daysRemaining": 5,
    "estimatedDays": 3.3,
    "buffer": 1.8,
    "isBusinessDays": true
  }
}
```

---

## ✅ **Benefits:**

1. **Realistickejšie** - Ľudia nepracujú cez víkend
2. **Presnejšie warnings** - Nezahŕňa víkendové dni do rezervy
3. **Lepšie plánovanie** - Tím vidí skutočné časové okno

---

## 🧪 **Testovanie:**

Spusti test script:
```bash
python backend/test_business_days.py
```

Výsledky:
- ✅ Pondelok-Piatok: 5 dní
- ✅ Pondelok-Nedeľa: 5 dní (víkend excluded)
- ✅ Víkend only: 0 dní
- ✅ 10 kalendárnych dní: ~7-8 pracovných dní

---

## 🔧 **Konfigurácia:**

V `risk_analyzer.py`:
```python
DEADLINE_BUFFER_DAYS = 3  # Warn if less than 3 WORKING days buffer
```

Táto konštanta definuje minimálnu rezervu v **pracovných dňoch**.

---

## 📝 **Poznámky:**

- **Státne sviatky** nie sú zatiaľ implementované (môže sa pridať v budúcnosti)
- **Časové pásma** - používa UTC
- **Presnosť** - normalizuje na začiatok dňa pre konzistentný výpočet

