import { Container } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import { YentaChat } from "@/components/Chat/YentaChat"

export const Route = createFileRoute("/_layout/yenta")({
  component: Yenta,
})

function Yenta() {
  return (
    <Container maxW="full">
      <YentaChat />
    </Container>
  )
} 