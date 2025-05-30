import { Box, VStack, HStack,  Button, Text, Flex } from "@chakra-ui/react"
import { useColorModeValue } from "../../components/ui/color-mode"
import { useState } from "react"
import * as React from "react"
import { MentionsInput, Mention } from 'react-mentions'
import { useQuery } from "@tanstack/react-query"
import { UsersService } from "@/client"

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
  const mentionBg = useColorModeValue("blue.100", "blue.900")
  const mentionTextColor = useColorModeValue("blue.800", "blue.100")


  // Fetch all users to map connection IDs to user info
  const { data: allUsers } = useQuery({
    queryKey: ["allUsers"],
    queryFn: () => UsersService.readUsers(),
  })

  // Get connected users
  const connectedUsers = React.useMemo(() => {
    if (!allUsers) return []
    
    return allUsers.data
      .map(user => ({
        id: user.id,
        display: user.full_name || user.email,
      }))
  }, [allUsers])

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message)
      setMessage("")
    }
  }

  const renderMessageContent = (content: string) => {
    return (
      <MentionsInput
        value={content}
        readOnly
        style={{
          control: {
            backgroundColor: 'transparent',
            color: textColor,
            border: 'none',
            padding: 0,
            minHeight: 'auto',
            width: '100%',
          },
          input: {
            color: textColor,
            margin: 0,
            padding: 0,
            width: '100%',
            minHeight: 'auto',
          },
          suggestions: {
            display: 'none',
          },
          '&singleLine': {
            display: 'inline-block',
            width: '100%',
          },
          '&multiLine': {
            input: {
              height: 'auto',
              overflow: 'auto',
            },
          },
        }}
      >
        <Mention
          trigger="@"
          data={connectedUsers}
          style={{
            backgroundColor: mentionBg,
            color: mentionTextColor,
            padding: '2px 4px',
            borderRadius: '4px',
          }}
        />
      </MentionsInput>
    );
  };

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
              {renderMessageContent(msg.content)}
            </Box>
          ))}
          <HStack mt={4}>
            <Box flex={1}>
              <MentionsInput
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                style={{
                  control: {
                    backgroundColor: inputBg,
                    color: textColor,
                    borderRadius: 'md',
                    border: `1px solid ${borderColor}`,
                    padding: '8px',
                    minHeight: '40px',
                    width: '100%',
                  },
                  input: {
                    color: textColor,
                    margin: 0,
                    padding: 0,
                    width: '100%',
                    minHeight: '24px',
                  },
                  suggestions: {
                    backgroundColor: bgColor,
                    border: `1px solid ${borderColor}`,
                    borderRadius: 'md',
                    marginTop: '4px',
                  },
                  '&singleLine': {
                    display: 'inline-block',
                    width: '100%',
                  },
                  '&multiLine': {
                    input: {
                      height: 'auto',
                      overflow: 'auto',
                    },
                  },
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
              >
                <Mention
                  trigger="@"
                  data={connectedUsers}
                  style={{
                    backgroundColor: mentionBg,
                    color: mentionTextColor,
                    padding: '2px 4px',
                    borderRadius: '4px',
                  }}
                />
              </MentionsInput>
            </Box>
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