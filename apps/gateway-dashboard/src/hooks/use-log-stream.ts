'use client'

import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { useQueryClient } from '@tanstack/react-query'

export function useLogStream(enabled: boolean = true) {
  const [isConnected, setIsConnected] = useState(false)
  const queryClient = useQueryClient()

  useEffect(() => {
    if (!enabled) return

    const socket: Socket = io('/?XTransformPort=3003', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
    })

    socket.on('connect', () => {
      console.log('[LogStream] Connected')
      setIsConnected(true)
    })

    socket.on('logs:new', (_log: unknown) => {
      // Invalidate the logs query to refetch with new data
      queryClient.invalidateQueries({ queryKey: ['logs'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    })

    socket.on('disconnect', () => {
      console.log('[LogStream] Disconnected')
      setIsConnected(false)
    })

    return () => {
      socket.disconnect()
    }
  }, [enabled, queryClient])

  return {
    isConnected,
  }
}
