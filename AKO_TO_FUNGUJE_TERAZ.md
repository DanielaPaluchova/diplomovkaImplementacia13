# 🎯 Ako funguje Smart Sprint Planning po fixe

## Scenár: Projekt má aktívny sprint

### 1️⃣ Začiatok - Vidíš oranžový banner

```
┌──────────────────────────────────────────────────────────┐
│ ⚠️  Active Sprint Detected: "Sprint 3 - Payment & Analytics" │
│                                                            │
│ To apply a new sprint plan, you must close the active     │
│ sprint first.                                              │
│                                                            │
│ → Check the option below to automatically close the        │
│   active sprint when applying:                            │
│                                                            │
│ ☐ Close active sprint when applying                       │
└──────────────────────────────────────────────────────────┘
```

### 2️⃣ Vygeneruješ plán (klikneš "Generate Plan")

✅ Plán sa vygeneruje normálne  
✅ Uvidíš zoznam navrhnutých taskov

### 3️⃣ Chceš aplikovať - Tlačidlo "Apply Plan" je ZABLOKOVANÉ

```
┌────────────────────┐
│  Apply Plan        │  <- Šedé, neaktívne
└────────────────────┘
```

Keď naň najedeš myšou, uvidíš tooltip:
```
┌──────────────────────────────────────────────┐
│ Cannot apply: Sprint "Sprint 3 - Payment    │
│ & Analytics" is currently active. Please     │
│ enable "Close active sprint when applying"   │
│ option in the warning banner above.          │
└──────────────────────────────────────────────┘
```

### 4️⃣ Zaškrtneš checkbox v banneri

```
┌──────────────────────────────────────────────────────────┐
│ ⚠️  Active Sprint Detected: "Sprint 3 - Payment & Analytics" │
│                                                            │
│ To apply a new sprint plan, you must close the active     │
│ sprint first.                                              │
│                                                            │
│ → Check the option below to automatically close the        │
│   active sprint when applying:                            │
│                                                            │
│ ☑ Close active sprint when applying  <- ZAŠKRTNUTÉ!       │
└──────────────────────────────────────────────────────────┘
```

### 5️⃣ Tlačidlo "Apply Plan" sa aktivuje

```
┌────────────────────┐
│  Apply Plan        │  <- Zelené, aktívne
└────────────────────┘
```

### 6️⃣ Klikneš na "Apply Plan" - Jasný dialóg

```
┌───────────────────────────────────────────────┐
│ Apply Sprint Plan                             │
├───────────────────────────────────────────────┤
│                                               │
│ This will create "Sprint 5" with 2 tasks     │
│ and assign them to team members.              │
│                                               │
│ ✓ The active sprint "Sprint 3 - Payment &    │
│   Analytics" will be closed and marked as    │
│   completed.                                  │
│                                               │
│ Continue?                                     │
│                                               │
│         [CANCEL]          [OK]                │
└───────────────────────────────────────────────┘
```

### 7️⃣ Klikneš OK - Výsledok

✅ Starý sprint sa uzavrie (status = 'completed')  
✅ Vytvorí sa nový sprint (status = 'active')  
✅ Tasky sa priradia k novému sprintu  
✅ **Tasky SÚ VIDITEĽNÉ v projekte!**

---

## 🚫 Čo sa NEMÔŽE stať

❌ **Nemôžeš omylom vytvoriť druhý aktívny sprint**
- Tlačidlo Apply je zablokované ak nemáš zaškrtnuté checkbox

❌ **Nemôžeš byť zmätená či sa sprint vytvorí alebo nie**
- Dialóg jasne povie čo sa stane
- Apply tlačidlo je buď dostupné (zelené) alebo zablokované (šedé)

❌ **Nemôžeš kliknúť OK a dostať chybu**
- Backend validácia je tam ako záchranná sieť
- Ale frontend ťa k tomu ani nedovolí dostať

---

## 💡 Zhrnutie

| Stav | Apply tlačidlo | Čo môžeš urobiť |
|------|----------------|-----------------|
| ❌ Nemáš zaškrtnuté "Close active sprint" | 🚫 ZABLOKOVANÉ (šedé) | Musíš zaškrtnúť checkbox |
| ✅ Máš zaškrtnuté "Close active sprint" | ✅ AKTÍVNE (zelené) | Môžeš kliknúť a aplikovať |

**VŽDY je jasné čo sa stane!** 🎉



