/**
 * TypeScript type definitions for GithubMirrorLink component
 */

import type { MirrorConfig } from './config';

/**
 * Props for the main GithubMirrorLink component
 */
export interface GithubMirrorLinkProps {
  /** Display text for the trigger link */
  text: string;
  /** GitHub resource URL to mirror */
  link: string;
  /** Whether to show WeChat public account option */
  oneDriveSupport?: boolean;
}

/**
 * Props for the MirrorCard component
 */
export interface MirrorCardProps {
  /** Mirror configuration */
  mirror: MirrorConfig;
  /** Full URL to mirror */
  fullUrl: string;
  /** Callback when copy is clicked */
  onCopy: (url: string) => Promise<void>;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Props for the MirrorSection component
 */
export interface MirrorSectionProps {
  /** Section title */
  title: string;
  /** Section icon/emoji */
  icon: string;
  /** Mirror cards to render */
  children: React.ReactNode;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Props for the Toast component
 */
export interface ToastProps {
  /** Whether toast is visible */
  visible: boolean;
  /** Message to display */
  message: string;
  /** Optional duration in milliseconds (default: 2000) */
  duration?: number;
  /** Callback when toast should be hidden */
  onHide?: () => void;
}

/**
 * Props for the QRCodeModal component
 */
export interface QRCodeModalProps {
  /** Whether QR code modal is visible */
  visible: boolean;
  /** Callback to close modal */
  onClose: () => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * Toast state for managing copy feedback
 */
export interface ToastState {
  visible: boolean;
  message: string;
}

/**
 * Section configuration for organizing mirrors
 */
export interface SectionConfig {
  /** Section title */
  title: string;
  /** Section icon */
  icon: string;
  /** Mirrors in this section */
  mirrors: MirrorConfig[];
}
