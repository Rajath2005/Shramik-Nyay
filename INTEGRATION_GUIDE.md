# 🚀 Integration Guide - New UI Components

## Overview

This guide shows how to integrate the new design system and Worker mode components into the existing Shramik Nyay application.

## 📋 Prerequisites

### 1. Install Dependencies

First, install all required dependencies:

```bash
cd frontend

# Core animation and UI
npm install motion lucide-react

# Utility libraries  
npm install class-variance-authority clsx tailwind-merge

# Radix UI components
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tooltip @radix-ui/react-progress

# Additional utilities
npm install sonner canvas-confetti use-debounce @tanstack/react-virtual
```

### 2. Import Design Tokens

Add to `frontend/src/index.css` or `main.tsx`:

```css
@import './styles/tokens.css';
@import './styles/animations.css';
```

---

## 🎯 Worker Mode Integration

### Current Structure

The Worker mode UI is currently embedded in `App.tsx` (lines 672+). Here's how to modernize it:

### Step 1: Add Welcome Screen

Before the main worker flow, add a welcome screen for first-time users:

```tsx
import { WelcomeScreen } from './components/ui/WelcomeScreen';

// In App component, add state:
const [showWelcome, setShowWelcome] = useState(() => 
  !localStorage.getItem('shramik:has-visited')
);

// In Worker mode render:
if (showWelcome) {
  return (
    <WelcomeScreen
      onGetStarted={() => {
        localStorage.setItem('shramik:has-visited', 'true');
        setShowWelcome(false);
      }}
      language={displayLanguage}
      copy={{
        welcomeTitle: copy.welcomeTitle || 'श्रमिक-न्याय',
        welcomeDescription: copy.welcomeDescription || 'Voice-led wage claim assistance',
        getStarted: copy.getStarted || 'Get Started',
        howItWorks: copy.howItWorks || 'How It Works',
        step1Title: copy.step1Title || 'Speak Your Details',
        step1Description: copy.step1Description || 'Answer questions in Hindi, Kannada, or English',
        step2Title: copy.step2Title || 'Review Your Claim',
        step2Description: copy.step2Description || 'Check all information for accuracy',
        step3Title: copy.step3Title || 'Submit & Download',
        step3Description: copy.step3Description || 'Get your official Form-A PDF',
      }}
    />
  );
}
```

### Step 2: Replace Question Display with QuestionCard

Replace the current `.workerQuestion` section:

```tsx
import { QuestionCard } from './components/ui/QuestionCard';

// Transform field data
const questionFields = FIELD_KEYS.map((key, index) => ({
  label: fields[index][0],
  value: session.slots[key] ? String(session.slots[key]) : null,
  verified: isSlotVerified(session.slots[key]),
}));

// Replace current question display with:
<QuestionCard
  question={currentQuestion}
  fields={questionFields}
  currentFieldIndex={firstMissing}
  totalFields={FIELD_KEYS.length}
  completedFields={done}
  online={session.online}
  connectionState={session.connectionState}
  copy={{
    allDetailsCollected: copy.allDetailsCollected,
    readyToReview: copy.readyToReview || 'Ready to review your claim',
    progressLabel: copy.progressLabel,
    connected: copy.connected || 'Connected',
    connecting: copy.connecting,
    reconnecting: copy.reconnecting,
  }}
/>
```

### Step 3: Replace Acoustic Orb with VoiceOrb

Replace the `AcousticOrb` component and its surrounding container:

```tsx
import { VoiceOrb } from './components/ui/VoiceOrb';

// Replace the entire .voiceCore section with:
<VoiceOrb
  active={orbActive}
  levels={waveform}
  state={mic.live ? 'listening' : workerPhase}
  stateText={
    mic.live
      ? copy.workerListening
      : workerPhase === 'thinking'
        ? copy.workerThinking
        : workerPhase === 'speaking'
          ? copy.workerSpeaking
          : copy.workerReady
  }
  hint={
    sample && session.consentState !== 'awaiting'
      ? copy.sampleMicHint
      : session.consentState !== 'awaiting' && !mic.live && workerPhase === 'idle'
        ? copy.micHint
        : undefined
  }
  showTelemetry={true}
/>
```

### Step 4: Replace Microphone Button

Replace the current `.workerMic` button:

```tsx
import { MicrophoneButton } from './components/ui/MicrophoneButton';

<MicrophoneButton
  isRecording={mic.live}
  disabled={(!canUseMicrophone && !mic.live) || workerPhase === 'thinking'}
  state={workerError ? 'error' : mic.live ? 'listening' : workerPhase}
  onClick={toggleMicrophone}
  ariaLabel={mic.live ? copy.stopRecording : copy.speakAnswer}
/>
```

### Step 5: Replace Text Input with TypeInputField

Replace the `.workerTyping` section:

```tsx
import { TypeInputField } from './components/ui/TypeInputField';

{session.consentState !== 'awaiting' && (
  <TypeInputField
    value={typed}
    onChange={setTyped}
    onSubmit={() => {
      if (typed.trim()) {
        setWorkerPhase('thinking');
        send({ type: 'utterance', text: typed.trim() });
        setTyped('');
      }
    }}
    placeholder={copy.typeAnswer}
    disabled={!session.online || session.serviceUnavailable}
    copy={{
      typeInstead: copy.typeInstead,
      typeAnswer: copy.typeAnswer,
      sendAnswer: copy.sendAnswer,
    }}
  />
)}
```

---

## 🎨 Using Base UI Components

### Button Component

```tsx
import { Button } from './components/ui/Button';

// Primary button
<Button onClick={handleClick}>Submit</Button>

// With variants
<Button variant="secondary">Cancel</Button>
<Button variant="outline">Edit</Button>
<Button variant="ghost">Skip</Button>
<Button variant="destructive">Delete</Button>

// With sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>

// Loading state
<Button loading disabled>Processing...</Button>

// Icon button
<Button variant="ghost" size="sm">
  <RefreshIcon />
</Button>
```

### Badge Component

```tsx
import { Badge } from './components/ui/Badge';

<Badge>Default</Badge>
<Badge variant="success">Verified</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>

// With dot indicator
<Badge variant="primary" dot>Live</Badge>

// Sizes
<Badge size="sm">Small</Badge>
<Badge size="lg">Large</Badge>
```

### Card Component

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './components/ui/Card';

<Card>
  <CardHeader>
    <CardTitle>Claim Details</CardTitle>
    <CardDescription>Review your wage claim information</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Your content */}
  </CardContent>
  <CardFooter>
    <Button>Continue</Button>
  </CardFooter>
</Card>
```

### Input Component

```tsx
import { Input } from './components/ui/Input';

<Input
  type="text"
  label="UAN Number"
  placeholder="Enter your UAN"
  value={uan}
  onChange={(e) => setUan(e.target.value)}
  helperText="12-digit Universal Account Number"
/>

// With error
<Input
  type="email"
  label="Email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error="Invalid email address"
/>

// With icons
<Input
  type="search"
  placeholder="Search..."
  leftIcon={<SearchIcon />}
  rightIcon={<ClearIcon onClick={handleClear} />}
/>
```

### Progress Component

```tsx
import { Progress, CircularProgress } from './components/ui/Progress';

// Linear progress
<Progress value={done} max={totalFields} variant="primary" />

// Circular progress
<CircularProgress value={75} size="lg" variant="success" />

// Indeterminate (loading)
<Progress indeterminate />
```

### Skeleton Component

```tsx
import { Skeleton, ShimmerWrapper } from './components/ui/Skeleton';

// Basic skeleton
<Skeleton variant="text" />
<Skeleton variant="circular" width={40} height={40} />
<Skeleton variant="rectangular" width={200} height={100} />

// With shimmer effect
<ShimmerWrapper>
  <Skeleton variant="text" />
  <Skeleton variant="text" />
</ShimmerWrapper>
```

### Tooltip Component

```tsx
import { Tooltip } from './components/ui/Tooltip';

<Tooltip content="This will delete your claim permanently">
  <Button variant="destructive">Delete</Button>
</Tooltip>

// Custom position
<Tooltip content="Save for later" position="left">
  <Button variant="ghost">Save</Button>
</Tooltip>
```

---

## 🎭 Using Animations & Springs

### Motion Springs

```tsx
import { motion } from 'motion/react';
import { springs } from './lib/springs';

// Smooth entrance
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={springs.smooth}
>
  Content
</motion.div>

// Bouncy button
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={springs.bouncy}
>
  Click me
</motion.button>

// Snappy toggle
<motion.div
  animate={{ x: isOn ? 20 : 0 }}
  transition={springs.snappy}
/>
```

### CSS Animations

```tsx
// In your CSS module:
.loading {
  animation: shimmer 2s infinite;
}

.success {
  animation: bounceIn 0.5s ease-out;
}

.error {
  animation: shake 0.4s ease-in-out;
}
```

---

## 📱 Haptic Feedback

```tsx
import { triggerHaptic } from './lib/haptics';

// Light tap
<Button onClick={() => {
  triggerHaptic('light');
  handleClick();
}}>
  Tap
</Button>

// Success feedback
const handleSuccess = () => {
  triggerHaptic('success');
  showSuccessMessage();
};

// Error feedback
const handleError = () => {
  triggerHaptic('error');
  showErrorMessage();
};
```

---

## 🛠️ Utilities

### Class Name Utility

```tsx
import { cn } from './lib/utils';

<div className={cn(
  'base-class',
  isActive && 'active-class',
  isError && 'error-class',
  className // User-provided className
)} />
```

### Format Currency

```tsx
import { formatCurrency } from './lib/utils';

const amount = formatCurrency(12500.50);
// Output: ₹12,500.50
```

### Debounce & Throttle

```tsx
import { debounce, throttle } from './lib/utils';

// Debounce search input
const debouncedSearch = debounce((query: string) => {
  performSearch(query);
}, 300);

// Throttle scroll handler
const throttledScroll = throttle(() => {
  updateScrollPosition();
}, 100);
```

---

## 🌐 Language Support

Add these to your `language.ts` COPY object:

```typescript
// For WelcomeScreen
welcomeTitle: string;
welcomeDescription: string;
getStarted: string;
howItWorks: string;
step1Title: string;
step1Description: string;
step2Title: string;
step2Description: string;
step3Title: string;
step3Description: string;

// For QuestionCard
readyToReview: string;
connected: string;

// For TypeInputField
(already exists: typeInstead, typeAnswer, sendAnswer)
```

---

## 🎨 Theming

All components automatically support dark mode through the design token system:

```tsx
// Theme is controlled by data-theme attribute on html element
document.documentElement.dataset.theme = 'dark'; // or 'light'
```

---

## ⚡ Performance Tips

1. **Lazy load heavy components:**
```tsx
const WelcomeScreen = lazy(() => import('./components/ui/WelcomeScreen'));
```

2. **Use Skeleton while loading:**
```tsx
{isLoading ? <Skeleton variant="rectangular" /> : <Component />}
```

3. **Virtualize long lists:**
```tsx
import { useVirtualizer } from '@tanstack/react-virtual';
```

4. **Optimize animations:**
```tsx
// Disable animations for reduced-motion preference
// Already handled in CSS with @media (prefers-reduced-motion: reduce)
```

---

## 🧪 Testing

After integration, test:

- ✅ All animations work smoothly
- ✅ Dark mode toggles correctly
- ✅ Haptic feedback works on mobile
- ✅ Accessibility (keyboard navigation, screen readers)
- ✅ Responsive design on all screen sizes
- ✅ Performance on low-end devices

---

## 📞 Next Steps

1. **Install Dependencies** - Run npm install commands
2. **Integrate Worker Mode** - Follow Worker Mode Integration above
3. **Test Integration** - Verify all components work
4. **Studio Mode** - Apply similar patterns to Studio mode
5. **Polish & Optimize** - Fine-tune animations and performance

---

## 🎯 Migration Checklist

- [ ] Install all npm dependencies
- [ ] Import design tokens in main CSS
- [ ] Add WelcomeScreen for first-time users
- [ ] Replace question display with QuestionCard
- [ ] Replace acoustic orb with VoiceOrb
- [ ] Replace mic button with MicrophoneButton
- [ ] Replace text input with TypeInputField
- [ ] Add language strings for new components
- [ ] Test on mobile and desktop
- [ ] Test dark mode
- [ ] Test accessibility
- [ ] Performance audit

---

Made with ❤️ for top-tier UI/UX
