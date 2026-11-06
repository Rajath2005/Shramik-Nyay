# 🎨 Component Gallery

Visual reference for all UI components in the Shramik Nyay design system.

---

## 🔘 Button Component

### Variants

```tsx
// Primary (default)
<Button>Primary Button</Button>
// Solid background, high emphasis

// Secondary
<Button variant="secondary">Secondary Button</Button>
// Softer background, medium emphasis

// Outline
<Button variant="outline">Outline Button</Button>
// Border only, low emphasis

// Ghost
<Button variant="ghost">Ghost Button</Button>
// No background, minimal

// Destructive
<Button variant="destructive">Delete</Button>
// Red, for dangerous actions

// Success
<Button variant="success">Confirm</Button>
// Green, for positive actions
```

### Sizes

```tsx
<Button size="xs">Extra Small</Button>
<Button size="sm">Small</Button>
<Button size="md">Medium</Button> // Default
<Button size="lg">Large</Button>
<Button size="xl">Extra Large</Button>
```

### States

```tsx
<Button loading disabled>Loading...</Button>
<Button disabled>Disabled</Button>
<Button>
  <Icon /> With Icon
</Button>
```

---

## 🏷️ Badge Component

### Variants

```tsx
<Badge>Default</Badge>           // Neutral gray
<Badge variant="primary">Primary</Badge>    // Blue
<Badge variant="success">Success</Badge>    // Green
<Badge variant="warning">Warning</Badge>    // Amber
<Badge variant="error">Error</Badge>        // Red
<Badge variant="outline">Outline</Badge>    // Border only
```

### Sizes

```tsx
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>  // Default
<Badge size="lg">Large</Badge>
```

### With Dot Indicator

```tsx
<Badge dot>Live</Badge>
<Badge variant="success" dot>Active</Badge>
```

---

## 🃏 Card Component

### Basic Card

```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Main card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Variants

```tsx
// Elevated (default)
<Card>Content</Card>

// Outlined
<Card variant="outline">Content</Card>

// Ghost (minimal)
<Card variant="ghost">Content</Card>
```

### Interactive Cards

```tsx
<Card
  interactive
  onClick={handleClick}
>
  Clickable card with hover effect
</Card>
```

---

## 📝 Input Component

### Basic Input

```tsx
<Input
  type="text"
  label="Label"
  placeholder="Enter text..."
  value={value}
  onChange={handleChange}
/>
```

### With Helper Text

```tsx
<Input
  label="Email"
  type="email"
  helperText="We'll never share your email"
/>
```

### With Error

```tsx
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>
```

### With Icons

```tsx
// Left icon
<Input
  leftIcon={<SearchIcon />}
  placeholder="Search..."
/>

// Right icon (clearable)
<Input
  value={value}
  onChange={handleChange}
  rightIcon={
    value && <ClearIcon onClick={() => setValue('')} />
  }
/>

// Both
<Input
  leftIcon={<UserIcon />}
  rightIcon={<CheckIcon />}
  placeholder="Username"
/>
```

### Sizes

```tsx
<Input size="sm" placeholder="Small" />
<Input size="md" placeholder="Medium" /> // Default
<Input size="lg" placeholder="Large" />
```

---

## 📊 Progress Component

### Linear Progress

```tsx
// Determinate
<Progress value={45} max={100} />

// Variants
<Progress value={45} variant="primary" />   // Blue
<Progress value={65} variant="success" />   // Green
<Progress value={85} variant="warning" />   // Amber
<Progress value={95} variant="error" />     // Red

// Indeterminate (loading)
<Progress indeterminate />
```

### Circular Progress

```tsx
// Basic
<CircularProgress value={75} />

// Sizes
<CircularProgress value={75} size="sm" />
<CircularProgress value={75} size="md" />
<CircularProgress value={75} size="lg" />

// Variants
<CircularProgress value={75} variant="success" />

// Indeterminate
<CircularProgress indeterminate />
```

---

## 💀 Skeleton Component

### Variants

```tsx
// Text skeleton (for paragraphs)
<Skeleton variant="text" />
<Skeleton variant="text" width="80%" />

// Circular (for avatars)
<Skeleton variant="circular" width={40} height={40} />

// Rectangular (for images, cards)
<Skeleton variant="rectangular" width={200} height={100} />
```

### With Shimmer Effect

```tsx
<ShimmerWrapper>
  <Skeleton variant="text" />
  <Skeleton variant="text" width="90%" />
  <Skeleton variant="text" width="70%" />
</ShimmerWrapper>
```

### Loading State Example

```tsx
{isLoading ? (
  <Card>
    <CardHeader>
      <Skeleton variant="text" width="40%" />
      <Skeleton variant="text" width="60%" />
    </CardHeader>
    <CardContent>
      <Skeleton variant="rectangular" height={200} />
    </CardContent>
  </Card>
) : (
  <Card>
    {/* Actual content */}
  </Card>
)}
```

---

## 💬 Tooltip Component

### Basic Tooltip

```tsx
<Tooltip content="Helpful information">
  <Button>Hover me</Button>
</Tooltip>
```

### Positions

```tsx
<Tooltip content="Top tooltip" position="top">
  <Button>Top</Button>
</Tooltip>

<Tooltip content="Bottom tooltip" position="bottom">
  <Button>Bottom</Button>
</Tooltip>

<Tooltip content="Left tooltip" position="left">
  <Button>Left</Button>
</Tooltip>

<Tooltip content="Right tooltip" position="right">
  <Button>Right</Button>
</Tooltip>
```

### With Delay

```tsx
<Tooltip content="Appears after 500ms" delay={500}>
  <Button>Delayed</Button>
</Tooltip>
```

---

## 🎤 Worker Mode Components

### WelcomeScreen

```tsx
<WelcomeScreen
  onGetStarted={handleStart}
  language="hi-IN"
  copy={{
    welcomeTitle: "श्रमिक-न्याय",
    welcomeDescription: "Voice-led wage claim assistance in your language",
    getStarted: "शुरू करें",
    howItWorks: "यह कैसे काम करता है",
    step1Title: "बोलें",
    step1Description: "अपनी जानकारी हिंदी, कन्नड़ या अंग्रेजी में बताएं",
    step2Title: "समीक्षा करें",
    step2Description: "सभी जानकारी की सटीकता की जांच करें",
    step3Title: "जमा करें",
    step3Description: "अपना आधिकारिक फॉर्म-ए पीडीएफ प्राप्त करें",
  }}
/>
```

**Features:**
- Animated logo entrance
- Step-by-step cards with icons
- Trust indicators (secure, GDPR, encrypted)
- Language badge
- Smooth transitions

---

### QuestionCard

```tsx
<QuestionCard
  question="आपका नाम क्या है?"
  fields={[
    { label: "Name", value: "John Doe", verified: true },
    { label: "UAN", value: null, verified: false },
    // ...more fields
  ]}
  currentFieldIndex={1}
  totalFields={8}
  completedFields={1}
  online={true}
  connectionState="connected"
  copy={{
    allDetailsCollected: "सभी विवरण एकत्रित",
    readyToReview: "समीक्षा के लिए तैयार",
    progressLabel: "प्रगति",
    connected: "जुड़ा हुआ",
    connecting: "जुड़ रहा है",
    reconnecting: "पुनः जुड़ रहा है",
  }}
/>
```

**Features:**
- Large, readable question
- Progress bar with completed/total
- Field list with active/completed states
- Connection status indicator
- Smooth state transitions

---

### VoiceOrb

```tsx
<VoiceOrb
  active={isListening}
  levels={audioLevels}
  state="listening" // 'idle' | 'listening' | 'thinking' | 'speaking' | 'error'
  stateText="सुन रहे हैं..."
  hint="अपना जवाब बोलें"
  showTelemetry={true}
/>
```

**Features:**
- Canvas-based acoustic visualization
- 36-ray waveform with audio levels
- Pulsing halo effects
- State-based colors
- Telemetry chips (8000 Hz, VAD, etc.)

---

### MicrophoneButton

```tsx
<MicrophoneButton
  isRecording={false}
  state="idle" // 'idle' | 'listening' | 'thinking' | 'error'
  onClick={handleToggleMic}
  ariaLabel="Start recording"
/>
```

**Features:**
- Circular gradient design
- Ripple effect on click
- Pulse rings when recording
- Recording indicator dot
- Haptic feedback
- State-based colors (blue/red/amber)
- Smooth scale animations

---

### TypeInputField

```tsx
<TypeInputField
  value={typedAnswer}
  onChange={setTypedAnswer}
  onSubmit={handleSubmit}
  placeholder="अपना जवाब टाइप करें..."
  disabled={false}
  copy={{
    typeInstead: "बजाय टाइप करें",
    typeAnswer: "जवाब टाइप करें",
    sendAnswer: "भेजें",
  }}
/>
```

**Features:**
- Collapsible design (toggle button → full form)
- Smooth expand/collapse animation
- Textarea with auto-focus
- Send button with icon
- Disabled state support

---

## 🎨 Color Tokens

### Primary Colors

```css
--color-primary-50   // Very light blue
--color-primary-100
--color-primary-200
--color-primary-300
--color-primary-400
--color-primary-500  // Base blue
--color-primary-600
--color-primary-700
--color-primary-800
--color-primary-900  // Very dark blue
--color-primary-950
```

### Semantic Colors

```css
--color-success-500  // Green
--color-warning-500  // Amber
--color-error-500    // Red
```

### Neutral Scale

```css
--color-neutral-0    // Pure white
--color-neutral-50
--color-neutral-100
...
--color-neutral-900  // Very dark
--color-neutral-950  // Almost black
```

---

## 🎭 Animation Presets

### Spring Animations

```tsx
import { springs } from './lib/springs';

// Snappy - Quick, responsive (buttons, toggles)
transition: springs.snappy

// Smooth - Balanced, general purpose
transition: springs.smooth

// Bouncy - Playful, attention-grabbing
transition: springs.bouncy

// Gentle - Slow, graceful
transition: springs.gentle

// Stiff - Very quick, minimal overshoot
transition: springs.stiff
```

### CSS Animations

```css
/* Loading */
animation: shimmer 2s infinite;
animation: pulse 2s infinite;

/* Entrance */
animation: fadeIn 0.3s ease-out;
animation: slideUp 0.3s ease-out;
animation: scaleIn 0.3s ease-out;

/* Interaction */
animation: bounceIn 0.5s ease-out;
animation: ripple 0.6s ease-out;

/* Attention */
animation: shake 0.4s ease-in-out;
animation: glow 2s ease-in-out infinite;
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile first approach */

/* Small devices (360px+) - Default */

/* Medium devices (768px+) */
@media (min-width: 768px) { }

/* Large devices (1024px+) */
@media (min-width: 1024px) { }

/* Extra large devices (1280px+) */
@media (min-width: 1280px) { }

/* Studio mode (1920×1080) */
@media (min-width: 1920px) { }
```

---

## ♿ Accessibility Features

### Keyboard Navigation
- All interactive components are keyboard accessible
- Focus visible styles
- Proper tab order

### Screen Readers
- ARIA labels on all components
- Live regions for dynamic content
- Semantic HTML

### Motion Preferences
```css
@media (prefers-reduced-motion: reduce) {
  /* Animations disabled or simplified */
}
```

### Color Contrast
```css
@media (prefers-contrast: high) {
  /* Increased contrast ratios */
}
```

---

## 💡 Usage Examples

### Loading State Pattern

```tsx
{isLoading ? (
  <ShimmerWrapper>
    <Skeleton variant="rectangular" height={200} />
    <Skeleton variant="text" />
    <Skeleton variant="text" width="80%" />
  </ShimmerWrapper>
) : (
  <Card>
    <CardContent>{content}</CardContent>
  </Card>
)}
```

### Form with Validation

```tsx
<form onSubmit={handleSubmit}>
  <Input
    label="UAN Number"
    value={uan}
    onChange={(e) => setUan(e.target.value)}
    error={errors.uan}
    helperText="12-digit number"
  />
  
  <Button
    type="submit"
    loading={isSubmitting}
    disabled={!isValid}
  >
    Submit
  </Button>
</form>
```

### Status Indicators

```tsx
<div>
  <Badge variant={status === 'verified' ? 'success' : 'warning'} dot>
    {status}
  </Badge>
  
  <Progress
    value={completionPercentage}
    variant={completionPercentage === 100 ? 'success' : 'primary'}
  />
</div>
```

---

Made with precision for Shramik Nyay 🎯
