import { Box, VStack, HStack, Input, Button, Text, Flex } from "@chakra-ui/react"
import { useColorModeValue } from "../../components/ui/color-mode"
import { useState } from "react"
import * as React from "react"

interface Message {
  content: string
  sender_id?: string
  role?: 'user' | 'yenta'
}

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isSending: boolean
  currentUserId?: string
  title?: string
  sidebar?: React.ReactNode
}

export function ChatInterface({
  messages,
  onSendMessage,
  isSending,
  currentUserId,
  title,
  sidebar,
}: ChatInterfaceProps) {
  const [message, setMessage] = useState("")

  // Colors
  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const inputBg = useColorModeValue("gray.50", "gray.900")
  const sidebarBg = useColorModeValue("gray.50", "gray.900")
  const sidebarActiveBg = useColorModeValue("gray.100", "gray.700")

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message)
      setMessage("")
    }
  }

  return (
    <Flex height="calc(100vh - 64px)">
      {/* Sidebar */}
      {sidebar && (
        <Box w="260px" bg={sidebarBg} borderRight="1px" borderColor={borderColor} p={4}>
          {sidebar}
        </Box>
      )}
      {/* Main chat area */}
      <Flex flex={1} direction="column" p={4} bg={bgColor}>
        {title && (
          <>
            <Text fontSize="2xl" fontWeight="bold" color={textColor} mb={4}>
              {title}
            </Text>
            <Box mb={4} height="1px" bg={borderColor} />
          </>
        )}
        <VStack gap={4} align="stretch" flex={1}>
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              p={2}
              bg={inputBg}
              borderRadius="md"
              alignSelf={
                (currentUserId && msg.sender_id === currentUserId) || msg.role === 'user'
                  ? "flex-end"
                  : "flex-start"
              }
              color={textColor}
            >
              {msg.content}
            </Box>
          ))}
          <HStack mt={4}>
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              bg={inputBg}
              color={textColor}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <Button
              colorScheme="blue"
              onClick={handleSend}
              loading={isSending}
              disabled={!message.trim()}
            >
              Send
            </Button>
          </HStack>
        </VStack>
      </Flex>
    </Flex>
  )
} 