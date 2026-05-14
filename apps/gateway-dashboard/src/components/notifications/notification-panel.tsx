'use client'

import { useKimariStore } from '@/lib/store'
import {
  useNotifications,
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
  type NotificationItem,
} from '@/hooks/use-api'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Bell, Info, AlertTriangle, XCircle, CheckCircle2, CheckCheck } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

function getRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function getDateGroup(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  return 'Earlier'
}

function NotificationIcon({ type }: { type: NotificationItem['type'] }) {
  switch (type) {
    case 'info':
      return <Info className="h-4 w-4 text-cyan-500" />
    case 'warning':
      return <AlertTriangle className="h-4 w-4 text-amber-500" />
    case 'error':
      return <XCircle className="h-4 w-4 text-red-500" />
    case 'success':
      return <CheckCircle2 className="h-4 w-4 text-emerald-500" />
  }
}

function getTypeBg(type: NotificationItem['type']): string {
  switch (type) {
    case 'info':
      return 'bg-cyan-500/10 border-cyan-500/20'
    case 'warning':
      return 'bg-amber-500/10 border-amber-500/20'
    case 'error':
      return 'bg-red-500/10 border-red-500/20'
    case 'success':
      return 'bg-emerald-500/10 border-emerald-500/20'
  }
}

function NotificationCard({
  notification,
  onMarkRead,
}: {
  notification: NotificationItem
  onMarkRead: (id: string) => void
}) {
  return (
    <motion.button
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      onClick={() => {
        if (!notification.read) onMarkRead(notification.id)
      }}
      className={cn(
        'w-full text-left glass-card depth-shadow rounded-lg p-4 transition-all card-hover-lift',
        !notification.read && 'border-l-2',
        getTypeBg(notification.type)
      )}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 shrink-0">
          <NotificationIcon type={notification.type} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              'text-sm font-medium truncate',
              !notification.read ? 'text-foreground' : 'text-muted-foreground'
            )}>
              {notification.title}
            </span>
            {!notification.read && (
              <span className="shrink-0 h-2 w-2 rounded-full bg-primary" />
            )}
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2 mb-1.5">
            {notification.message}
          </p>
          <div className="flex items-center gap-2 text-[10px] text-muted-foreground/70">
            <span>{getRelativeTime(notification.createdAt)}</span>
            <span>·</span>
            <span className="capitalize">{notification.source}</span>
          </div>
        </div>
      </div>
    </motion.button>
  )
}

export function NotificationPanel() {
  const { notificationsOpen, setNotificationsOpen } = useKimariStore()
  const { data } = useNotifications()
  const markRead = useMarkNotificationRead()
  const markAllRead = useMarkAllNotificationsRead()

  const notifications = data?.notifications ?? []
  const unreadCount = data?.unreadCount ?? 0

  // Group notifications by date
  const groups: { label: string; items: NotificationItem[] }[] = []
  const groupMap = new Map<string, NotificationItem[]>()

  for (const n of notifications) {
    const group = getDateGroup(n.createdAt)
    if (!groupMap.has(group)) {
      groupMap.set(group, [])
    }
    groupMap.get(group)!.push(n)
  }

  const groupOrder = ['Today', 'Yesterday', 'Earlier']
  for (const label of groupOrder) {
    const items = groupMap.get(label)
    if (items && items.length > 0) {
      groups.push({ label, items })
    }
  }

  return (
    <Sheet open={notificationsOpen} onOpenChange={setNotificationsOpen}>
      <SheetContent side="right" className="w-[380px] sm:max-w-[420px] p-0 flex flex-col">
        <SheetHeader className="p-6 pb-4 border-b border-border/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <SheetTitle className="text-lg font-semibold">Notifications</SheetTitle>
              {unreadCount > 0 && (
                <span className="flex items-center justify-center h-5 min-w-5 px-1.5 rounded-full bg-primary text-primary-foreground text-[10px] font-bold">
                  {unreadCount}
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => markAllRead.mutate()}
                className="h-7 text-xs text-muted-foreground hover:text-foreground btn-press"
              >
                <CheckCheck className="h-3.5 w-3.5 mr-1" />
                Mark all read
              </Button>
            )}
          </div>
          <SheetDescription className="text-xs text-muted-foreground">
            {unreadCount > 0
              ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}`
              : 'All caught up!'}
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="flex-1">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
              <div className="h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center mb-4">
                <Bell className="h-6 w-6 text-muted-foreground/50" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">No notifications</p>
              <p className="text-xs text-muted-foreground/60">
                You&apos;ll see alerts about server events, model downloads, and system updates here.
              </p>
            </div>
          ) : (
            <div className="p-4 space-y-6">
              <AnimatePresence>
                {groups.map((group) => (
                  <div key={group.label}>
                    <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 px-1">
                      {group.label}
                    </h3>
                    <div className="space-y-2">
                      {group.items.map((notification) => (
                        <NotificationCard
                          key={notification.id}
                          notification={notification}
                          onMarkRead={(id) => markRead.mutate(id)}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}
