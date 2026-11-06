import { toast as sonnerToast, Toaster, type ExternalToast } from 'sonner';
import { triggerHaptic } from './haptics';

// Re-export Toaster for easy import
export { Toaster };

interface ToastOptions extends ExternalToast {
  haptic?: boolean;
}

/**
 * Show a success toast notification
 */
export function toastSuccess(message: string, options?: ToastOptions) {
  const { haptic = true, ...restOptions } = options || {};
  
  if (haptic) {
    triggerHaptic('success');
  }
  
  return sonnerToast.success(message, {
    duration: 4000,
    ...restOptions,
  });
}

/**
 * Show an error toast notification
 */
export function toastError(message: string, options?: ToastOptions) {
  const { haptic = true, ...restOptions } = options || {};
  
  if (haptic) {
    triggerHaptic('error');
  }
  
  return sonnerToast.error(message, {
    duration: 5000,
    ...restOptions,
  });
}

/**
 * Show a warning toast notification
 */
export function toastWarning(message: string, options?: ToastOptions) {
  const { haptic = true, ...restOptions } = options || {};
  
  if (haptic) {
    triggerHaptic('medium');
  }
  
  return sonnerToast.warning(message, {
    duration: 4000,
    ...restOptions,
  });
}

/**
 * Show an info toast notification
 */
export function toastInfo(message: string, options?: ToastOptions) {
  const { haptic = false, ...restOptions } = options || {};
  
  if (haptic) {
    triggerHaptic('light');
  }
  
  return sonnerToast.info(message, {
    duration: 3000,
    ...restOptions,
  });
}

/**
 * Show a loading toast notification
 */
export function toastLoading(message: string, options?: ExternalToast) {
  return sonnerToast.loading(message, {
    duration: Infinity,
    ...options,
  });
}

/**
 * Show a promise toast (automatically handles loading, success, error states)
 */
export function toastPromise<T>(
  promise: Promise<T>,
  messages: {
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((error: Error) => string);
  },
  options?: ToastOptions
) {
  const { haptic = true, ...restOptions } = options || {};
  
  const wrappedPromise = promise
    .then((data) => {
      if (haptic) triggerHaptic('success');
      return data;
    })
    .catch((error) => {
      if (haptic) triggerHaptic('error');
      throw error;
    });
  
  return sonnerToast.promise(wrappedPromise, { ...messages, ...restOptions });
}

/**
 * Dismiss a specific toast by ID
 */
export function toastDismiss(toastId?: string | number) {
  sonnerToast.dismiss(toastId);
}

/**
 * Custom toast with full control
 */
export function toast(message: string, options?: ToastOptions) {
  const { haptic = false, ...restOptions } = options || {};
  
  if (haptic) {
    triggerHaptic('light');
  }
  
  return sonnerToast(message, {
    duration: 3000,
    ...restOptions,
  });
}

// Re-export the raw toast for advanced usage
export { sonnerToast as rawToast };
