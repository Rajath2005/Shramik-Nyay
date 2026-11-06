# ⚡ Quick Reference Card

Essential commands and imports for rapid development.

---

## 🚀 Setup Commands

```bash
# Install dependencies
cd frontend
npm install motion lucide-react class-variance-authority clsx tailwind-merge @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tooltip @radix-ui/react-progress sonner canvas-confetti use-debounce @tanstack/react-virtual
```

---

## 📦 Common Imports

### Base Components
```tsx
import {
  Button,
  Badge,
  Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter,
  Input,
  Progress, CircularProgress,
  Skeleton, ShimmerWrapper,
  Tooltip,
} from './components/ui';
```

### Worker Mode
```tsx
import {
  WelcomeScreen,
  QuestionCard,
  VoiceOrb,
  MicrophoneButton,
  TypeInputField,
} from './components/ui';
```

### Studio Mode
```tsx
import {
  StudioHeader,
  StudioPanel, StudioGrid,
  InfoCard, InfoCardGrid,
  StatCard, StatCardGrid,
} from './components/ui';
```

### Utilities
```tsx
import { cn } from './lib/utils';
import { springs } from './lib/springs';
import { triggerHaptic } from './lib/haptics';
import { toastSuccess, toastError, toastWarning, toastInfo, Toaster } from './lib/toast';
import { motion } from 'motion/react';
```

---

## 🎨 Common Patterns

### Button
```tsx
<Button variant="primary" size="lg" onClick={handler}>
  Click Me
</Button>
```

### Card
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

### Input with Error
```tsx
<Input
  label="Email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={errors.email}
  helperText="We'll never share"
/>
```

### Progress
```tsx
<Progress value={done} max={total} variant="success" />
```

### Loading Skeleton
```tsx
{loading ? (
  <Skeleton variant="rectangular" height={200} />
) : (
  <YourContent />
)}
```

### Toast Notification
```tsx
toastSuccess('Success!', { description: 'Action completed' });
toastError('Error!', { description: error.message });
```

### Motion Animation
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={springs.smooth}
>
  Content
</motion.div>
```

### Haptic Feedback
```tsx
<button onClick={() => {
  triggerHaptic('light');
  handleClick();
}}>
  Tap me
</button>
```

---

## 🎭 Variants Quick Reference

### Button Variants
`primary` `secondary` `outline` `ghost` `destructive` `success`

### Button Sizes
`xs` `sm` `md` `lg` `xl`

### Badge Variants
`default` `primary` `success` `warning` `error` `outline`

### Card Variants
`elevated` `outline` `ghost`

### Progress Variants
`primary` `success` `warning` `error`

### Skeleton Variants
`text` `circular` `rectangular`

---

## 🎨 Color Tokens

```css
/* Primary */
var(--color-primary-50)
var(--color-primary-500) /* Base */
var(--color-primary-900)

/* Success */
var(--color-success-500)

/* Warning */
var(--color-warning-500)

/* Error */
var(--color-error-500)

/* Neutral */
var(--color-neutral-0)    /* White */
var(--color-neutral-50)   /* Very light */
var(--color-neutral-500)  /* Medium */
var(--color-neutral-900)  /* Very dark */
var(--color-neutral-950)  /* Almost black */
```

---

## 📏 Spacing

```css
var(--spacing-1)   /* 4px */
var(--spacing-2)   /* 8px */
var(--spacing-3)   /* 12px */
var(--spacing-4)   /* 16px */
var(--spacing-6)   /* 24px */
var(--spacing-8)   /* 32px */
var(--spacing-12)  /* 48px */
var(--spacing-16)  /* 64px */
```

---

## 🎯 Animation Presets

```tsx
springs.snappy  // Quick, responsive
springs.smooth  // Balanced
springs.bouncy  // Playful
springs.gentle  // Slow, graceful
springs.stiff   // Very quick
```

---

## 📱 Breakpoints

```css
/* Mobile first */
@media (min-width: 768px) { }   /* Tablet */
@media (min-width: 1024px) { }  /* Desktop */
@media (min-width: 1280px) { }  /* Large Desktop */
@media (min-width: 1920px) { }  /* Studio */
```

---

## ♿ Accessibility

```tsx
// Focus visible
className={cn(styles.button, 'focus-visible:outline-2')}

// ARIA label
<button aria-label="Close dialog">

// Live region
<div aria-live="polite" aria-atomic="true">

// Hidden but accessible
<span className="visually-hidden">
```

---

## 🔧 Utility Functions

### Class Names
```tsx
cn('base-class', condition && 'conditional-class', className)
```

### Format Currency
```tsx
formatCurrency(12500.50) // ₹12,500.50
```

### Debounce
```tsx
const debouncedSearch = debounce((query) => search(query), 300);
```

### Throttle
```tsx
const throttledScroll = throttle(() => handleScroll(), 100);
```

---

## 🎬 Common Layouts

### Two-Column Studio Layout
```tsx
<StudioGrid columns={2} gap="lg">
  <div>{/* Left column */}</div>
  <div>{/* Right column */}</div>
</StudioGrid>
```

### Info Card Grid
```tsx
<InfoCardGrid columns={3}>
  <InfoCard label="Name" value={name} />
  <InfoCard label="UAN" value={uan} mono />
  <InfoCard label="Status" value="Verified" status="verified" />
</InfoCardGrid>
```

### Stat Card Grid
```tsx
<StatCardGrid columns={4}>
  <StatCard
    label="Total"
    value={total}
    icon={<Icon />}
    iconVariant="success"
    change={{ value: 12.5, label: 'vs last month' }}
  />
</StatCardGrid>
```

---

## 🎨 Theme Toggle

```tsx
// In your app
const [dark, setDark] = useState(false);

useEffect(() => {
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
}, [dark]);

<button onClick={() => setDark(!dark)}>
  Toggle Theme
</button>
```

---

## 📋 Checklist Template

```tsx
// Worker Mode Integration
- [ ] Install dependencies
- [ ] Import tokens & animations CSS
- [ ] Add Toaster to app root
- [ ] Replace question display → QuestionCard
- [ ] Replace microphone → MicrophoneButton
- [ ] Replace orb → VoiceOrb
- [ ] Replace text input → TypeInputField
- [ ] Add WelcomeScreen

// Studio Mode Integration
- [ ] Replace header → StudioHeader
- [ ] Wrap sections → StudioPanel
- [ ] Convert slots → InfoCard grid
- [ ] Add metrics → StatCard grid
- [ ] Add notifications → Toast

// Polish
- [ ] Add loading states
- [ ] Add error states
- [ ] Test keyboard navigation
- [ ] Test dark mode
- [ ] Test mobile responsive
- [ ] Accessibility audit
```

---

## 🐛 Common Issues & Fixes

### Issue: Components not styled
**Fix:** Import CSS tokens in main.tsx
```tsx
import './styles/tokens.css';
import './styles/animations.css';
```

### Issue: Motion not working
**Fix:** Install motion package
```bash
npm install motion
```

### Issue: Dark mode not working
**Fix:** Set data-theme on html element
```tsx
document.documentElement.dataset.theme = 'dark';
```

### Issue: Toasts not showing
**Fix:** Add Toaster to app root
```tsx
import { Toaster } from './lib/toast';

function App() {
  return (
    <>
      <Toaster />
      {/* Your app */}
    </>
  );
}
```

---

## 📚 Documentation Files

- **INTEGRATION_GUIDE.md** - Step-by-step integration
- **COMPONENT_GALLERY.md** - All components with examples
- **STUDIO_MODE_EXAMPLE.md** - Complete Studio mode example
- **TRANSFORMATION_SUMMARY.md** - Complete overview
- **IMPLEMENTATION_STATUS.md** - Progress tracking

---

**⚡ Quick Tip:** Keep this file open while coding for instant reference!
