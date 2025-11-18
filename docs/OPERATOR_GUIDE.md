# Capsule Pins - Factory Operator Guide
**Week 16: DAC Factory Complete System**

A comprehensive guide for factory workers and operators using the Capsule Pins system for real-time industrial intelligence.

---

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Understanding Capsules](#understanding-capsules)
3. [Daily Operations](#daily-operations)
4. [AR/VR Mode](#arvr-mode)
5. [Responding to Alerts](#responding-to-alerts)
6. [Troubleshooting](#troubleshooting)
7. [Safety Guidelines](#safety-guidelines)

---

## 🚀 **Getting Started**

### **Accessing the System**

**Web Browser (Desktop/Tablet):**
1. Open your web browser (Chrome, Edge, Safari)
2. Navigate to: `https://your-factory-url.com`
3. Log in with your credentials
4. You'll see the Capsule Pins dashboard

**Mobile App (Android):**
1. Download "Capsule Pins" from Google Play Store
2. Open the app
3. Log in with your credentials
4. Grant camera and location permissions (for AR features)

**Desktop App (Windows/Mac/Linux):**
1. Launch "Capsule Pins" from your desktop
2. Log in with your credentials
3. The app will connect to your factory's system

### **First-Time Setup**

1. **Profile Setup:**
   - Click your name in the top-right corner
   - Go to "Settings"
   - Set your preferred language
   - Configure notification preferences

2. **Notification Preferences:**
   - **Critical Alerts:** Always enabled (cannot disable)
   - **Warnings:** Recommended to enable
   - **Info Updates:** Optional
   - **Sound:** Enable/disable alert sounds

3. **AR/VR Setup (Optional):**
   - Go to "Settings" → "AR/VR Mode"
   - Follow the calibration wizard
   - Test gesture controls

---

## 💊 **Understanding Capsules**

### **What is a Capsule?**

A **capsule** is a smart alert that represents an actionable insight from your factory equipment. Think of it as a "task card" that tells you:
- **What** is happening (e.g., "Motor overheating")
- **Where** it's happening (e.g., "Assembly Line 3")
- **How urgent** it is (priority level)
- **What actions** you can take

### **Capsule Status Colors**

| Color | Status | Meaning | Action Required |
|-------|--------|---------|-----------------|
| 🔴 **Red** | Critical | Immediate attention needed | Stop and address now |
| 🟡 **Amber** | Warning | Issue developing | Monitor and plan action |
| 🟢 **Green** | Active | Normal operation | Routine monitoring |
| 🔵 **Blue** | Resolved | Issue fixed | Review for learning |
| ⚫ **Gray** | Dismissed | Acknowledged, no action | None |

### **Priority Levels**

- **P1 (Critical):** Stop work, address immediately
- **P2 (High):** Address within 1 hour
- **P3 (Medium):** Address within shift
- **P4 (Low):** Address when convenient
- **P5 (Info):** For awareness only

### **Capsule Components**

Each capsule shows:
1. **Title:** Brief description of the issue
2. **Source:** Which sensor/equipment triggered it
3. **Metrics:** Real-time data (temperature, pressure, etc.)
4. **Actions:** Buttons for what you can do
5. **Consensus Badge:** ✅ = Validated by AI system

---

## 🏭 **Daily Operations**

### **Morning Routine**

**1. Check Dashboard (5 minutes)**
```
✓ Review overnight capsules
✓ Check critical alerts (red)
✓ Acknowledge warnings (amber)
✓ Review resolved issues from previous shift
```

**2. Handoff from Previous Shift**
- Read shift notes in "Resolved" capsules
- Check for any pending maintenance
- Review production targets

### **During Shift**

**Monitoring:**
- Keep dashboard visible on your station
- Respond to new capsules within 5 minutes
- Update capsule status after taking action

**Best Practices:**
- ✅ Acknowledge capsules immediately
- ✅ Add notes when taking action
- ✅ Escalate if unsure
- ❌ Don't dismiss without reading
- ❌ Don't ignore critical alerts

### **End of Shift**

**1. Handoff Checklist:**
```
✓ Resolve or escalate all critical capsules
✓ Add notes to pending warnings
✓ Document any unusual events
✓ Brief next shift operator
```

**2. System Check:**
- Ensure all equipment sensors are online
- Report any connectivity issues
- Log out properly

---

## 🥽 **AR/VR Mode**

### **When to Use AR/VR**

**Use AR Mode when:**
- Working hands-free (wearing gloves)
- Need to see capsules overlaid on equipment
- Multiple capsules in same area
- Training new operators

**Use VR Mode when:**
- Remote monitoring from control room
- Reviewing historical data
- Planning maintenance routes

### **Gesture Controls**

**Basic Gestures (No Touch Required):**

1. **Point** 👉
   - Extend index finger
   - Point at capsule to highlight it
   - Capsule glows when selected

2. **Pinch** 🤏
   - Bring thumb and index finger together
   - Opens capsule details
   - Works from 1-3 meters away

3. **Open Palm** 🖐️
   - Show open palm to camera
   - Dismisses current capsule
   - Confirms "I've seen this"

4. **Thumbs Up** 👍
   - Give thumbs up gesture
   - Acknowledges capsule
   - Marks as "working on it"

5. **Closed Fist** ✊
   - Make a fist
   - Executes primary action
   - Use carefully (confirms action)

### **Voice Commands**

**Available Commands:**
- "Show critical" - Filter to critical capsules only
- "Hide capsule" - Dismiss current capsule
- "Acknowledge" - Acknowledge current capsule
- "Execute" - Execute primary action
- "Help" - Show command list

**Tips:**
- Speak clearly and loudly (85+ dB factory noise)
- Wait for confirmation beep
- Repeat if not recognized

### **AR/VR Safety**

⚠️ **IMPORTANT:**
- Never use AR/VR while operating machinery
- Stay aware of your surroundings
- Remove headset if you feel dizzy
- Take breaks every 30 minutes
- Report any discomfort to supervisor

---

## 🚨 **Responding to Alerts**

### **Critical Alerts (Red)**

**Step 1: STOP**
- Stop current work immediately
- Do not ignore critical alerts
- Alert nearby workers if needed

**Step 2: READ**
- Read capsule title and description
- Check metrics (temperature, pressure, etc.)
- Note equipment location

**Step 3: ACT**
- Click "Acknowledge" button
- Follow recommended action
- If unsure, click "Escalate"

**Step 4: UPDATE**
- Add notes on what you did
- Mark as "Resolved" when fixed
- If can't fix, escalate to maintenance

**Example: Motor Overheating**
```
1. Acknowledge capsule
2. Check motor temperature gauge
3. If >85°C: Emergency stop
4. If 80-85°C: Reduce load
5. Call maintenance if persists
6. Add notes: "Reduced load to 70%, temp dropped to 78°C"
7. Mark resolved when temp <75°C
```

### **Warning Alerts (Amber)**

**Step 1: ACKNOWLEDGE**
- Click "Acknowledge" within 15 minutes
- System tracks response time

**Step 2: ASSESS**
- Is this urgent? (Will it become critical?)
- Can I handle it now or later?
- Do I need help?

**Step 3: PLAN**
- If urgent: Handle immediately
- If not urgent: Schedule within shift
- If need help: Click "Escalate"

**Step 4: EXECUTE**
- Take recommended action
- Monitor metrics
- Update capsule status

**Example: High Pressure Alert**
```
1. Acknowledge: "I see this"
2. Check pressure gauge: 88 PSI (threshold: 85 PSI)
3. Assess: Not critical yet, but trending up
4. Action: Adjust relief valve
5. Monitor: Pressure drops to 82 PSI
6. Resolve: "Adjusted relief valve, pressure normalized"
```

### **Active Capsules (Green)**

These are informational - no immediate action required.

**What to do:**
- Review during routine checks
- Monitor trends
- Report patterns to supervisor

**Example: Production Line Optimal**
```
- Everything running normally
- Just confirms system is working
- No action needed
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Capsule Not Appearing**

**Symptoms:**
- Expected alert didn't show
- Sensor showing data but no capsule

**Solutions:**
```
✓ Check sensor connection (green light)
✓ Refresh browser (F5)
✓ Check "All Status" filter (not just "Critical")
✓ Verify you're logged in
✓ Contact IT if persists
```

#### **2. Can't Acknowledge Capsule**

**Symptoms:**
- "Acknowledge" button grayed out
- Click does nothing

**Solutions:**
```
✓ Check internet connection
✓ Refresh page
✓ Try different browser
✓ Check if capsule already acknowledged by someone else
✓ Contact supervisor if urgent
```

#### **3. AR/VR Gestures Not Working**

**Symptoms:**
- Pointing doesn't highlight capsules
- Gestures not recognized

**Solutions:**
```
✓ Check camera permissions (Settings → Privacy)
✓ Ensure good lighting (not too dark/bright)
✓ Remove gloves temporarily
✓ Recalibrate (Settings → AR/VR → Calibrate)
✓ Use touch controls as backup
```

#### **4. Too Many Capsules**

**Symptoms:**
- Dashboard overwhelmed with capsules
- Can't find critical ones

**Solutions:**
```
✓ Use "Critical" filter (red button)
✓ Sort by priority (P1 first)
✓ Acknowledge old capsules
✓ Escalate if genuinely overwhelmed
✓ Contact supervisor for help
```

#### **5. False Alarms**

**Symptoms:**
- Capsule triggered but no real issue
- Sensor reading incorrect

**Solutions:**
```
✓ Verify with physical gauge
✓ Mark as "Dismissed" with note: "False alarm - sensor issue"
✓ Report to maintenance
✓ Don't ignore - always verify first
```

---

## ⚠️ **Safety Guidelines**

### **General Safety**

1. **Always Prioritize Safety Over System**
   - If system says "safe" but you see danger → Trust your eyes
   - If system says "danger" but looks safe → Still investigate
   - When in doubt, stop and ask

2. **Emergency Situations**
   - Hit physical emergency stop first
   - Then acknowledge capsule
   - Never rely solely on digital alerts

3. **Personal Protective Equipment (PPE)**
   - Always wear required PPE
   - AR/VR headsets do NOT replace safety glasses
   - Remove headsets in hazardous areas

### **AR/VR Specific Safety**

⚠️ **DO NOT use AR/VR:**
- While operating machinery
- On elevated platforms
- Near moving equipment
- In areas with poor visibility
- When feeling unwell

✅ **DO use AR/VR:**
- In designated safe zones
- During equipment inspections (powered off)
- In control rooms
- For training (simulated environment)

### **Data Privacy**

- Never share your login credentials
- Log out when leaving workstation
- Don't photograph capsules with personal phone
- Report suspicious system behavior

---

## 📞 **Getting Help**

### **Who to Contact**

**For Urgent Issues (Critical Capsules):**
- Shift Supervisor: Ext. 1234
- Maintenance: Ext. 5678
- Safety Officer: Ext. 9999

**For System Issues:**
- IT Help Desk: Ext. 2222
- Email: support@your-factory.com

**For Training:**
- Training Coordinator: Ext. 3333
- Schedule refresher: training@your-factory.com

### **Escalation Process**

```
Level 1: You (Operator)
  ↓ (Can't resolve in 15 min)
Level 2: Shift Supervisor
  ↓ (Can't resolve in 1 hour)
Level 3: Maintenance Team
  ↓ (Can't resolve in 4 hours)
Level 4: Plant Manager
```

---

## 📚 **Quick Reference Card**

**Print this and keep at your workstation:**

```
╔══════════════════════════════════════════════════════════╗
║           CAPSULE PINS QUICK REFERENCE                   ║
╠══════════════════════════════════════════════════════════╣
║ STATUS COLORS:                                           ║
║   🔴 Critical → Stop & Act Now                           ║
║   🟡 Warning → Act Within 1 Hour                         ║
║   🟢 Active → Monitor                                    ║
║   🔵 Resolved → Review                                   ║
║                                                          ║
║ ACTIONS:                                                 ║
║   Acknowledge → "I see this"                             ║
║   Inspect → "I'm checking"                               ║
║   Mitigate → "I'm fixing"                                ║
║   Escalate → "I need help"                               ║
║   Resolve → "It's fixed"                                 ║
║                                                          ║
║ AR/VR GESTURES:                                          ║
║   Point 👉 → Highlight                                   ║
║   Pinch 🤏 → Open                                        ║
║   Open Palm 🖐️ → Dismiss                                ║
║   Thumbs Up 👍 → Acknowledge                             ║
║   Fist ✊ → Execute                                      ║
║                                                          ║
║ EMERGENCY:                                               ║
║   Physical E-Stop First!                                 ║
║   Then acknowledge capsule                               ║
║   Call: Ext. 9999                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

## 📝 **Glossary**

- **Capsule:** Smart alert representing actionable insight
- **Consensus:** AI validation (✅ badge = verified by multiple systems)
- **PCT:** Probability of Consensus Truth (confidence score)
- **Shadow Twin:** Digital replica of physical equipment
- **Sensor:** Device that measures equipment metrics
- **MQTT:** Communication protocol for sensor data
- **WebSocket:** Real-time connection to server

---

## 📄 **Version History**

- **v1.0** (Week 16) - Initial operator guide
- Complete DAC Factory system
- AR/VR gesture controls
- Shadow Twin consensus validation

---

**Questions? Contact your shift supervisor or IT help desk.**

**Stay safe, stay informed, stay productive!** 🏭✨
