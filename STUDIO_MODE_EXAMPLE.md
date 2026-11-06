# 🎬 Studio Mode Integration Example

Complete example showing how to use the new Studio components to create a professional 1920×1080 interface.

## Layout Structure

```tsx
import {
  StudioHeader,
  StudioPanel,
  StudioGrid,
  InfoCard,
  InfoCardGrid,
  StatCard,
  StatCardGrid,
} from './components/ui';

function StudioMode() {
  return (
    <div className="studio-container">
      {/* Header with glassmorphism */}
      <StudioHeader
        mode="studio"
        onModeChange={setMode}
        dark={dark}
        onThemeChange={toggleTheme}
        language={language}
        onLanguageChange={setLanguage}
        online={session.online}
        connectionState={session.connectionState}
        serviceMode={session.mode}
        liveUsage={session.liveUsage}
        copy={copy}
      />

      {/* Main Grid Layout - 2 columns */}
      <StudioGrid columns={2} gap="lg" className="studio-main-grid">
        
        {/* Left Column - Audio & Transcript */}
        <div className="studio-left-column">
          
          {/* Audio Panel */}
          <StudioPanel
            title="Audio Control"
            subtitle="8000 Hz • MONO • VAD 0.72"
            variant="glass"
            actions={
              <>
                <Button variant="ghost" size="sm" onClick={toggleMic}>
                  {micLive ? 'Stop' : 'Start'}
                </Button>
                <Button variant="ghost" size="sm" onClick={playSample}>
                  Sample
                </Button>
              </>
            }
          >
            {/* Audio visualization, waveform, controls */}
            <AudioVisualization
              levels={waveform}
              micLive={micLive}
              telemetry={session.telemetry}
            />
          </StudioPanel>

          {/* Transcript Panel */}
          <StudioPanel
            title="Transcript"
            subtitle={`Detected: ${detectedLanguage}`}
            variant="elevated"
            footer={
              <div className="transcript-stats">
                <span>Latency: {session.latency}ms</span>
                <Badge variant="success">Active</Badge>
              </div>
            }
          >
            {/* Transcript content */}
            <TranscriptContent
              transcript={session.transcript}
              boostedWords={session.biasWords}
            />
          </StudioPanel>

        </div>

        {/* Right Column - Claim Data & Form */}
        <div className="studio-right-column">
          
          {/* Stats Overview */}
          <StatCardGrid columns={4}>
            <StatCard
              label="Completion"
              value={`${done}/${totalFields}`}
              icon={<CheckCircleIcon />}
              iconVariant="success"
              change={{ value: 25, label: 'vs last claim' }}
            />
            <StatCard
              label="Arrears"
              value={formatCurrency(session.audit?.principal_arrears_inr)}
              icon={<CurrencyIcon />}
              iconVariant="primary"
              accent
            />
            <StatCard
              label="Latency"
              value={`${session.latency}ms`}
              icon={<TimerIcon />}
              iconVariant="warning"
              footer="Average response time"
            />
            <StatCard
              label="Confidence"
              value="98.5%"
              icon={<TrendingUpIcon />}
              iconVariant="success"
              change={{ value: 2.3, label: 'improvement' }}
            />
          </StatCardGrid>

          {/* Claim Slots Panel */}
          <StudioPanel
            title="Claim Details"
            subtitle={`${done} of ${totalFields} fields completed`}
            actions={
              <Progress value={done} max={totalFields} variant="success" />
            }
          >
            <InfoCardGrid columns={2}>
              {FIELD_KEYS.map((key, index) => (
                <InfoCard
                  key={key}
                  label={fields[index][0]}
                  value={session.slots[key]}
                  status={
                    isSlotVerified(session.slots[key])
                      ? 'verified'
                      : index === firstMissing
                        ? 'pending'
                        : undefined
                  }
                  hint={fields[index][1]}
                  mono={key === 'uan' || key === 'mobile'}
                />
              ))}
            </InfoCardGrid>

            {/* UAN Input */}
            {!session.slots.uan && (
              <div className="uan-input-section">
                <Input
                  label="UAN Number"
                  value={uan}
                  onChange={(e) => setUan(e.target.value)}
                  placeholder="Enter 12-digit UAN"
                  helperText="Universal Account Number"
                />
                <Button
                  onClick={() => send({ type: 'uan', value: uan })}
                  disabled={!uan.trim()}
                >
                  Verify UAN
                </Button>
              </div>
            )}
          </StudioPanel>

          {/* Paper Form Panel */}
          <StudioPanel
            title="Form Draft"
            subtitle={session.pdfUrl ? 'Ready for download' : 'Draft only'}
            footer={
              session.audit && (
                <div className="form-actions">
                  <Button
                    variant="primary"
                    onClick={prepareDraft}
                    disabled={!session.audit}
                  >
                    Prepare Draft
                  </Button>
                  {session.pdfUrl && (
                    <>
                      <Button
                        variant="outline"
                        onClick={() => window.open(session.pdfUrl)}
                      >
                        Download PDF
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.open(session.jsonUrl)}
                      >
                        Download JSON
                      </Button>
                    </>
                  )}
                </div>
              )
            }
          >
            <PaperForm
              copy={copy}
              fields={fields}
              slots={session.slots}
              audit={session.audit}
              studio
            />

            {/* Consent Bar */}
            {session.audit && (
              <ConsentBar
                copy={copy}
                state={session.consentState}
                voiceConsentRecorded={session.voiceConsentRecorded}
                readback={session.readback}
                language={displayLanguage}
                audioUrl={session.timbreAudioUrl}
                pdfUrl={session.pdfUrl}
                jsonUrl={session.jsonUrl}
                onPrepare={prepareDraft}
                onDelete={session.deleteClaim}
                deletingClaim={session.deletingClaim}
              />
            )}
          </StudioPanel>

        </div>
      </StudioGrid>
    </div>
  );
}
```

---

## CSS for Layout

```css
.studio-container {
  min-height: 100vh;
  background: linear-gradient(
    to bottom,
    var(--color-neutral-50),
    var(--color-neutral-100)
  );
  padding-bottom: var(--spacing-8);
}

[data-theme='dark'] .studio-container {
  background: linear-gradient(
    to bottom,
    var(--color-neutral-950),
    var(--color-neutral-900)
  );
}

.studio-main-grid {
  max-width: 1920px;
  margin: 0 auto;
  padding: var(--spacing-6);
}

.studio-left-column,
.studio-right-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.transcript-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: var(--font-size-sm);
  color: var(--color-neutral-600);
}

[data-theme='dark'] .transcript-stats {
  color: var(--color-neutral-400);
}

.uan-input-section {
  display: flex;
  gap: var(--spacing-3);
  align-items: flex-end;
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--color-neutral-200);
}

[data-theme='dark'] .uan-input-section {
  border-top-color: var(--color-neutral-800);
}

.form-actions {
  display: flex;
  gap: var(--spacing-3);
  width: 100%;
}

@media (max-width: 1440px) {
  .studio-main-grid {
    padding: var(--spacing-4);
  }
}

@media (max-width: 1024px) {
  .studio-main-grid {
    grid-template-columns: 1fr !important;
  }
}
```

---

## Audio Visualization Component Example

```tsx
function AudioVisualization({ levels, micLive, telemetry }) {
  return (
    <div className="audio-viz-container">
      {/* Telemetry Chips */}
      <div className="telemetry-row">
        <Badge variant="outline" size="sm">8000 Hz • MONO</Badge>
        <Badge variant="outline" size="sm">1024 B / 64 ms</Badge>
        <Badge variant={micLive ? 'success' : 'outline'} size="sm" dot={micLive}>
          {micLive ? 'Recording' : 'Ready'}
        </Badge>
      </div>

      {/* Waveform Canvas */}
      <canvas
        ref={canvasRef}
        className="waveform-canvas"
        width={800}
        height={200}
      />

      {/* Noise Level Control */}
      <div className="noise-control">
        <label>Noise Threshold</label>
        <input
          type="range"
          min="0"
          max="100"
          value={noiseLevel}
          onChange={(e) => onNoiseLevelChange(Number(e.target.value))}
        />
        <span>{noiseLevel}%</span>
      </div>

      {/* Telemetry Data */}
      {telemetry && (
        <div className="telemetry-grid">
          <InfoCard
            label="Samples"
            value={telemetry.samples}
            mono
            compact
          />
          <InfoCard
            label="VAD Score"
            value={telemetry.vad.toFixed(2)}
            mono
            compact
          />
          <InfoCard
            label="Buffer"
            value={`${telemetry.buffer}%`}
            mono
            compact
          />
        </div>
      )}
    </div>
  );
}
```

---

## Transcript Component Example

```tsx
function TranscriptContent({ transcript, boostedWords }) {
  if (!transcript || transcript.length === 0) {
    return (
      <div className="transcript-empty">
        <p>No transcript yet. Start speaking to see your words here.</p>
      </div>
    );
  }

  return (
    <div className="transcript-list">
      {transcript.map((item, index) => (
        <motion.div
          key={index}
          className="transcript-item"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <div className="transcript-meta">
            <Badge variant="outline" size="sm">
              {item.timestamp}
            </Badge>
            <Badge variant="primary" size="sm">
              {item.confidence}% confidence
            </Badge>
          </div>
          <p className="transcript-text">
            {highlightBoostedWords(item.text, boostedWords)}
          </p>
        </motion.div>
      ))}
    </div>
  );
}
```

---

## Toast Notifications Usage

```tsx
import { toastSuccess, toastError, toastWarning, toastPromise } from './lib/toast';

// Success notification
function handleClaimSubmit() {
  toastSuccess('Claim submitted successfully!', {
    description: 'Your Form-A PDF is ready for download',
  });
}

// Error notification
function handleError(error: Error) {
  toastError('Failed to submit claim', {
    description: error.message,
    action: {
      label: 'Retry',
      onClick: () => retrySubmit(),
    },
  });
}

// Warning notification
function handleIncompleteData() {
  toastWarning('Some fields are missing', {
    description: 'Please complete all required fields',
  });
}

// Promise toast (auto-handles loading/success/error)
async function submitClaim() {
  toastPromise(
    submitClaimAPI(),
    {
      loading: 'Submitting your claim...',
      success: 'Claim submitted successfully!',
      error: (err) => `Failed: ${err.message}`,
    }
  );
}
```

---

## Example: Complete Studio Panel with Real Data

```tsx
<StudioPanel
  title="Wage Claim Analysis"
  subtitle="Powered by Evon v3.3 Form-A Engine"
  variant="glass"
  actions={
    <>
      <Tooltip content="Refresh analysis">
        <Button variant="ghost" size="sm" onClick={refreshAnalysis}>
          <RefreshIcon />
        </Button>
      </Tooltip>
      <Button variant="outline" size="sm" onClick={exportData}>
        Export
      </Button>
    </>
  }
  footer={
    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
      <span>Last updated: {lastUpdated}</span>
      <Button variant="primary" onClick={generatePDF}>
        Generate Form-A PDF
      </Button>
    </div>
  }
>
  {/* Stats Grid */}
  <StatCardGrid columns={3}>
    <StatCard
      label="Principal Arrears"
      value={formatCurrency(session.audit?.principal_arrears_inr)}
      icon={<CurrencyIcon />}
      iconVariant="primary"
      accent
    />
    <StatCard
      label="Interest"
      value={formatCurrency(session.audit?.interest_inr)}
      icon={<PercentIcon />}
      iconVariant="success"
    />
    <StatCard
      label="Total Claim"
      value={formatCurrency(
        (session.audit?.principal_arrears_inr || 0) +
        (session.audit?.interest_inr || 0)
      )}
      icon={<SumIcon />}
      iconVariant="warning"
    />
  </StatCardGrid>

  {/* Detailed Info */}
  <div style={{ marginTop: 'var(--spacing-6)' }}>
    <h3 style={{ marginBottom: 'var(--spacing-4)' }}>Breakdown</h3>
    <InfoCardGrid columns={2}>
      <InfoCard
        label="From Date"
        value={session.audit?.employment_period_from}
        icon={<CalendarIcon />}
      />
      <InfoCard
        label="To Date"
        value={session.audit?.employment_period_to}
        icon={<CalendarIcon />}
      />
      <InfoCard
        label="Duration"
        value={calculateDuration(
          session.audit?.employment_period_from,
          session.audit?.employment_period_to
        )}
        icon={<ClockIcon />}
      />
      <InfoCard
        label="Monthly Wage"
        value={formatCurrency(session.audit?.monthly_wage_inr)}
        icon={<CurrencyIcon />}
        mono
      />
    </InfoCardGrid>
  </div>
</StudioPanel>
```

---

## Tips for Best Results

1. **Use Glassmorphism Sparingly** - Apply `variant="glass"` to header and key panels
2. **Organize with Grids** - Use StudioGrid, InfoCardGrid, StatCardGrid for consistent spacing
3. **Show Progress** - Use Progress bars and completion badges
4. **Provide Feedback** - Use toasts for user actions
5. **Keep it Clean** - Use empty states when no data
6. **Show Status** - Use status indicators on InfoCards
7. **Group Related Data** - Use panels to organize content
8. **Responsive by Default** - Components adapt to smaller screens

---

Made for professional Studio mode at 1920×1080 🎬
