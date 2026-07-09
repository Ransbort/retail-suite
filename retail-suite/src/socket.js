import { io } from "socket.io-client"

let socket = null

export function initSocket(siteName) {
  if (socket) return socket

  const host = window.location.origin

  socket = io(host, {
    path: "/socket.io",
    withCredentials: true,
    reconnectionAttempts: 5,
    transports: ["polling", "websocket"],
  })

  console.log("[socket] connecting to", host)

  socket.on("connect", () => {
    console.log("[socket] connected:", socket.id)
  })

  socket.on("connect_error", (err) => {
    console.error("[socket] error:", err.message)
  })

  socket.on("disconnect", (reason) => {
    console.log("[socket] disconnected:", reason)
  })

  return socket
}
