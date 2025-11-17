/**
 * Notification Service
 * Handles native system notifications for capsule alerts
 */

import { Notification, nativeImage } from 'electron';
import { join } from 'path';

export class NotificationService {
  private activeNotifications: Map<string, Notification> = new Map();

  /**
   * Show native notification
   */
  show(title: string, body: string, capsuleId?: string): void {
    // Create notification
    const notification = new Notification({
      title,
      body,
      icon: this.getIcon(),
      silent: false,
      timeoutType: 'default',
    });

    // Handle click
    notification.on('click', () => {
      console.log(`[Notification] Clicked: ${capsuleId || 'unknown'}`);
      
      // TODO: Show window and focus on capsule
      // mainWindow?.show();
      // mainWindow?.webContents.send('capsule:focus', { capsuleId });
    });

    // Handle close
    notification.on('close', () => {
      if (capsuleId) {
        this.activeNotifications.delete(capsuleId);
      }
    });

    // Show notification
    notification.show();

    // Store reference
    if (capsuleId) {
      this.activeNotifications.set(capsuleId, notification);
    }
  }

  /**
   * Close notification for capsule
   */
  close(capsuleId: string): void {
    const notification = this.activeNotifications.get(capsuleId);
    if (notification) {
      notification.close();
      this.activeNotifications.delete(capsuleId);
    }
  }

  /**
   * Close all notifications
   */
  closeAll(): void {
    for (const notification of this.activeNotifications.values()) {
      notification.close();
    }
    this.activeNotifications.clear();
  }

  /**
   * Get notification icon
   */
  private getIcon(): string {
    const iconPath = join(__dirname, '../../assets/notification-icon.png');
    return iconPath;
  }
}
