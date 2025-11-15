# RACI Workload - Rýchle Zhrnutie

## ❓ Otázka: Je RACI workload naprieč všetkými projektami alebo len pre jeden projekt?

## ✅ Odpoveď: **OBE VERZIE EXISTUJÚ!**

### 📊 RACI Workload (Current Project)

- Počíta **len aktuálny projekt**
- Užitočné pre optimalizáciu v rámci jedného projektu

### 🌍 RACI Cross-Project Workload

- Počíta **naprieč všetkými projektami**
- Kritické pre správne plánovanie a zabránenie preťaženiu

---

## 📊 Vizuálne Porovnanie

### Scenár: Sarah má úlohy v 3 projektoch

```
┌─────────────────────────────────────────────────────────────────┐
│                         SARAH'S WORKLOAD                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📦 E-Commerce Platform (aktuálne zobrazený)                    │
│     ├─ Payment Gateway (R) ......... 5.0 weighted SP            │
│     ├─ Checkout Flow (C) ........... 0.4 weighted SP            │
│     └─ Security Audit (I) .......... 0.03 weighted SP           │
│        Subtotal: 5.43 SP                                         │
│                                                                  │
│  📱 Mobile App                                                   │
│     ├─ Authentication (R) ........... 8.0 weighted SP            │
│     ├─ CI/CD Setup (A) .............. 0.5 weighted SP            │
│     └─ API Review (C) ............... 0.25 weighted SP           │
│        Subtotal: 8.75 SP                                         │
│                                                                  │
│  🖥️ Admin Dashboard                                              │
│     ├─ User Management (R) .......... 3.0 weighted SP            │
│     ├─ DB Schema (C) ................ 0.4 weighted SP            │
│     └─ Deployment (I) ............... 0.02 weighted SP           │
│        Subtotal: 3.42 SP                                         │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  TOTAL WEIGHTED SP: 17.6 SP                                      │
│  MAX CAPACITY:      20 SP                                        │
│                                                                  │
│  🎯 RACI WORKLOAD: 86%                                           │
│  ██████████████████░░░░░░░░░░░░░░░░░░░                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Čo Vidíte V Aplikácii

### 1️⃣ Na stránke "Requirement Changes" pre projekt "E-Commerce Platform"

```
┌────────────────────────────────────────────────┐
│  Current Project State                         │
├────────────────────────────────────────────────┤
│                                                │
│  📊 Project Workload                           │
│      27%                                       │
│      (Active sprint only)                      │
│      ↑ Len E-Commerce Platform                 │
│                                                │
│  🌐 Cross-Project Workload                     │
│      86%                                       │
│      (All active sprints)                      │
│      ↑ Všetky projekty                         │
│                                                │
│  👥 RACI Workload                              │
│      24%                                       │
│      (Active sprint - current project)         │
│      ↑ Len E-Commerce Platform + všetky RACI   │
│                                                │
│  🌍 RACI Cross-Project Workload                │
│      86%                                       │
│      (Active sprint across all projects)       │
│      ↑ Všetky projekty + všetky RACI           │
│                                                │
└────────────────────────────────────────────────┘
```

### 2️⃣ Na PERT + RACI Optimization stránke

```
┌────────────────────────────────────────┐
│  RACI Weighted Workload                │
│  (Active Sprint - All Projects)        │
├────────────────────────────────────────┤
│  Sarah Johnson   86%  ████████████░░   │
│  Emily Chen      92%  █████████████▓   │
│  John Smith      55%  ███████░░░░░░░   │
└────────────────────────────────────────┘
```

**Tooltip detail:**

```
✅ Sarah Johnson: 86%
   E-Commerce: 5.43 SP (27%)
   Mobile App: 8.75 SP (44%)
   Dashboard:  3.42 SP (17%)
   ─────────────────────────
   Total: 17.6 / 20 SP
```

---

## 🎯 Kľúčové Body

### ✅ RACI Workload (Current Project) počíta:

1. ✅ **Len aktuálny projekt**
2. ✅ **Všetky RACI role** (R, A, C, I)
3. ✅ **Váhy podľa rolí:**
   - Responsible (R): 100%
   - Accountable (A): 10%
   - Consulted (C): 5%
   - Informed (I): 1%
4. ✅ **Len aktívny sprint** aktuálneho projektu

### ✅ RACI Cross-Project Workload počíta:

1. ✅ **Všetky projekty** kde člen tímu pracuje
2. ✅ **Všetky RACI role** (R, A, C, I)
3. ✅ **Váhy podľa rolí:**
   - Responsible (R): 100%
   - Accountable (A): 10%
   - Consulted (C): 5%
   - Informed (I): 1%
4. ✅ **Aktívne sprinty** vo všetkých projektoch

### ❌ Obe verzie NEPOČÍTAJÚ:

- ❌ Budúce sprinty (len aktívne)
- ❌ Ukončené sprinty

---

## 💡 Prečo Je To Dôležité?

### Rozdiel medzi Project a Cross-Project RACI Workload:

#### 📊 RACI Workload (Current Project):

- Ukazuje ako veľmi je člen tímu zaťažený **v aktuálnom projekte**
- Užitočné pre **optimalizáciu v rámci jedného projektu**
- Príklad: Sarah má 24% RACI workload v E-Commerce projekte

#### 🌍 RACI Cross-Project Workload:

- Ukazuje **celkovú zaťaženosť** člena tímu naprieč **všetkými projektmi**
- Kritické pre **správne plánovanie** a zabránenie preťaženiu
- Príklad: Sarah má 86% RACI cross-project workload (E-Commerce + Mobile + Dashboard)

### Bez Cross-Project pohľadu:

```
Manažér: "Sarah má len 24% RACI workload v E-Commerce.
          Pridelím jej ešte 15 SP úloh s rôznymi RACI rolami."

Reality Check:
  Sarah má 86% RACI workload naprieč všetkými projektmi
  + 15 SP = 161% workload
  = 🔴 KRITICKÉ PREŤAŽENIE!
```

### S Cross-Project pohľadom:

```
Manažér: "Sarah má 86% RACI cross-project workload.
          Má len 14% voľnej kapacity.
          V E-Commerce má 24% RACI workload, môžem jej prideliť max 3 SP."

Reality Check:
  Sarah má 86% cross-project workload
  + 3 SP (weighted) = 96% workload
  = ✅ V poriadku, pod kapacitou
```

---

## 📍 Kde Nájdete Cross-Project Workload

| Stránka                      | Karty/Sekcie                     | Cross-Project?                            |
| ---------------------------- | -------------------------------- | ----------------------------------------- |
| **PERT + RACI Optimization** | RACI Weighted Workload           | ✅ Áno                                    |
| **PERT + RACI Optimization** | Active Sprint Table              | ✅ Áno (používa sa pre Adjusted Duration) |
| **Requirement Changes**      | Project Workload Card            | ⚠️ Single Project                         |
| **Requirement Changes**      | Cross-Project Workload Card      | ✅ Áno                                    |
| **Requirement Changes**      | RACI Workload Card               | ⚠️ Single Project                         |
| **Requirement Changes**      | RACI Cross-Project Workload Card | ✅ Áno                                    |
| **Project Detail**           | Team Workload                    | ⚠️ Single Project                         |

---

## 🔍 Ako To Overiť?

### Krok 1: Otvorte PERT + RACI Optimization stránku

```
1. Vyberte projekt (napr. "E-Commerce Platform")
2. Prejdite na tab "Active Sprint"
3. Pozrite sa na "RACI Weighted Workload" sekciu
```

### Krok 2: Skontrolujte tooltip

```
1. Najeďte myšou na Sarah Johnson v workload tabuľke
2. Tooltip zobrazí breakdown po projektoch
3. Uvidíte: E-Commerce (27%) + Mobile (44%) + Dashboard (17%) = 86%
```

### Krok 3: Porovnajte s Requirement Changes stránkou

```
1. Otvorte Requirement Changes stránku
2. Vyberte ten istý projekt
3. Uvidíte DVE RACI karty:

   a) "RACI Workload" karta:
      - Tooltip hovorí: "Active sprint - current project only"
      - Sarah má napr. 24% (len E-Commerce projekt)

   b) "RACI Cross-Project Workload" karta:
      - Tooltip hovorí: "Active sprint across all projects"
      - Sarah má 86% - zhoduje sa s PERT stránkou!
```

---

## 📚 Detailné Dokumenty

Pre viac informácií, pozrite:

1. **RACI_WORKLOAD_ANALYSIS.md**
   - Kompletná technická analýza
   - Frontend a backend kód
   - Konzistencia cez celú aplikáciu

2. **RACI_WORKLOAD_EXAMPLE.md**
   - Praktický príklad s konkrétnymi číslami
   - Porovnanie rôznych metód výpočtu
   - Dôsledky a odporúčania

---

## ✅ Finálna Odpoveď

### **Existujú DVA typy RACI Workload:**

#### 1️⃣ RACI Workload (Current Project)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ✅ Zahŕňa LEN aktuálny projekt                                 │
│  ✅ Zahŕňa VŠETKY RACI role (R, A, C, I)                        │
│  ✅ Používa váhy podľa úrovne zapojenia                         │
│  ✅ Užitočné pre optimalizáciu v rámci jedného projektu         │
│  📊 Zobrazuje sa na Requirement Changes stránke                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2️⃣ RACI Cross-Project Workload

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ✅ Zahŕňa VŠETKY projekty kde člen tímu pracuje                │
│  ✅ Zahŕňa VŠETKY RACI role (R, A, C, I)                        │
│  ✅ Používa váhy podľa úrovne zapojenia                         │
│  ✅ Konzistentné v celej aplikácii (frontend + backend)         │
│  ✅ Kritické pre správne rozhodnutia a zabránenie preťaženiu    │
│  🌍 Zobrazuje sa na Requirement Changes a PERT stránkach        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Dátum:** 2025-11-13  
**Verzia:** 2.0  
**Status:** ✅ AKTUALIZOVANÉ - Pridané obe verzie RACI Workload (Project + Cross-Project)
