import { Container } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import { YentaChat } from "@/components/Chat/YentaChat"
import { ChatLayout } from "@/components/Chat/ChatLayout"

export const Route = createFileRoute("/_layout/yenta")({
  component: Yenta,
})

function Yenta() {
  return (
    <ChatLayout>
      {({ selectedChatId, onSelectChat }) => (
        <YentaChat selectedChatId={selectedChatId} onSelectChat={onSelectChat} />
      )}
    </ChatLayout>
  )
}
