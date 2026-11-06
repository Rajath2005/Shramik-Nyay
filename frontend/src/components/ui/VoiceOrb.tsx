import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { springs } from '../../lib/springs';
import styles from './VoiceOrb.module.css';

interface VoiceOrbProps {
  active: boolean;
  levels: number[];
  state: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  stateText: string;
  hint?: string;
  showTelemetry?: boolean;
}

export function VoiceOrb({
  active,
  levels,
  state,
  stateText,
  hint,
  showTelemetry = false,
}: VoiceOrbProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    if (!context) return;
    
    let frame = 0;
    let animationFrame = 0;
    
    const render = () => {
      const dpr = window.devicePixelRatio || 1;
      const size = 300;
      
      if (canvas.width !== size * dpr) {
        canvas.width = size * dpr;
        canvas.height = size * dpr;
        canvas.style.width = `${size}px`;
        canvas.style.height = `${size}px`;
      }
      
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, size, size);
      
      const center = size / 2;
      const average = levels.length 
        ? levels.reduce((sum, level) => sum + level, 0) / levels.length 
        : 0;
      
      // Draw acoustic visualization
      for (let index = 0; index < 36; index += 1) {
        const angle = (index / 36) * Math.PI * 2 - Math.PI / 2;
        const source = levels[index % Math.max(levels.length, 1)] || 0;
        const wave = active 
          ? Math.abs(Math.sin(frame * 0.045 + index * 0.7)) * 0.55 
          : 0;
        const magnitude = 7 + (active 
          ? source * 22 + wave * 14 
          : 4 + Math.sin(frame * 0.018 + index) * 2);
        const inner = 105;
        const outer = inner + magnitude;
        
        const x1 = center + Math.cos(angle) * inner;
        const y1 = center + Math.sin(angle) * inner;
        const x2 = center + Math.cos(angle) * outer;
        const y2 = center + Math.sin(angle) * outer;
        
        context.beginPath();
        context.moveTo(x1, y1);
        context.lineTo(x2, y2);
        context.lineWidth = index % 3 === 0 ? 2.4 : 1.4;
        context.lineCap = 'round';
        
        // Color based on state
        if (state === 'error') {
          context.strokeStyle = `rgba(239, 68, 68, ${0.38 + Math.min(source + wave, 0.5)})`;
        } else if (active) {
          context.strokeStyle = `rgba(16, 185, 129, ${0.38 + Math.min(source + wave, 0.5)})`;
        } else {
          context.strokeStyle = `rgba(59, 130, 246, ${0.34 + Math.max(average, 0.08)})`;
        }
        
        context.stroke();
      }
      
      frame += 1;
      animationFrame = window.requestAnimationFrame(render);
    };
    
    render();
    
    return () => window.cancelAnimationFrame(animationFrame);
  }, [active, levels, state]);

  return (
    <div>
      {showTelemetry && (
        <motion.div
          className={styles.telemetryStatus}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springs.smooth}
        >
          <div className={styles.telemetryChip}>
            <span className={styles.telemetryDot} />
            8000 Hz • MONO
          </div>
          <div className={styles.telemetryChip}>1024 B / 64 ms</div>
          <div className={styles.telemetryChip}>VAD 0.72</div>
        </motion.div>
      )}

      <div className={`${styles.container} ${active ? styles.active : ''}`}>
        <span className={styles.halo} />
        <span className={styles.innerHalo} />
        <canvas
          ref={canvasRef}
          className={`${styles.orbCanvas} ${active ? styles.active : ''}`}
          aria-label={stateText}
          role="img"
        />
      </div>

      <motion.div
        className={styles.stateIndicator}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={springs.smooth}
      >
        <p
          className={`${styles.stateText} ${styles[state] || ''}`}
          role="status"
          aria-live="polite"
        >
          {stateText}
        </p>
        {hint && (
          <motion.p
            className={styles.stateHint}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springs.smooth, delay: 0.2 }}
          >
            {hint}
          </motion.p>
        )}
      </motion.div>
    </div>
  );
}
