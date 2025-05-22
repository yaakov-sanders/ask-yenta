import React, { useState } from "react"
import { Box, Button, Flex, Text } from "@chakra-ui/react"
import { useColorModeValue } from "../ui/color-mode"
import type { ReactNode } from "react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { YentaChatService } from "@/client/sdk.gen"
import type { YentaChatInfo, YentaChatsResponse } from "@/client/types.gen"
import { handleError } from "@/utils"

interface ChatLayoutProps {
  children: (props: { selectedChatId: string; onSelectChat: (id: string) => void }) => ReactNode
}

const PAGE_SIZE = 10

export const ChatLayout = ({ children }: ChatLayoutProps) => {
  // Dark mode aware colors
  const sidebarBg = useColorModeValue("white", "gray.900")
  const sidebarText = useColorModeValue("gray.800", "white")
  const mainBg = useColorModeValue("gray.50", "gray.900")
  const borderColor = useColorModeValue("gray.200", "gray.700")

  // Sidebar state
  const [page, setPage] = useState(0)
  const [selectedChatId, setSelectedChatId] = useState<string>("")

  // Fetch chat list with pagination
  const chatsQuery = useQuery<YentaChatsResponse>({
    queryKey: ["chats", { page, limit: PAGE_SIZE }],
    queryFn: YentaChatService.getChats,
  })

  // Create new chat
  const createChatMutation = useMutation({
    mutationFn: YentaChatService.createChat,
    onSuccess: (data) => {
      setSelectedChatId(data.conversation_id)
    },
    onError: (err) => handleError(err as any),
  })

  // Select first chat by default
  React.useEffect(() => {
    if (
      chatsQuery.data?.chats_info?.length &&
      !selectedChatId &&
      !createChatMutation.isPending
    ) {
      setSelectedChatId(chatsQuery.data.chats_info[0].conversation_id)
    }
  }, [chatsQuery.data, selectedChatId, createChatMutation.isPending])

  // Pagination logic
  const hasPrev = page > 0
  const hasNext =
    chatsQuery.data?.chats_info?.length === PAGE_SIZE // crude check

  // For chat highlight color
  const selectedBg = useColorModeValue("blue.100", "blue.700")
  const hoverBg = useColorModeValue("gray.100", "gray.700")

  return (
    <Flex h="100vh" w="100vw">
      {/* Sidebar */}
      <Box
        w="300px"
        bg={sidebarBg}
        color={sidebarText}
        p={4}
        display="flex"
        flexDirection="column"
        borderRightWidth="1px"
        borderColor={borderColor}
      >
        {/* New Chat Button */}
        <Button
          colorScheme="blue"
          mb={4}
          w="100%"
          onClick={() => createChatMutation.mutate()}
          loading={createChatMutation.isPending}
        >
          New Chat
        </Button>
        {/* Chat List */}
        <Box flex="1" overflowY="auto">
          {chatsQuery.isLoading ? (
            <Text>Loading...</Text>
          ) : (
            chatsQuery.data?.chats_info?.map((chat: YentaChatInfo, idx: number) => (
              <Box
                key={chat.conversation_id}
                mb={idx !== (chatsQuery.data?.chats_info?.length ?? 0) - 1 ? 2 : 0}
                p={2}
                borderRadius="md"
                bg={selectedChatId === chat.conversation_id ? selectedBg : "transparent"}
                cursor="pointer"
                onClick={() => setSelectedChatId(chat.conversation_id)}
                _hover={{ bg: hoverBg }}
              >
                <Text fontWeight={selectedChatId === chat.conversation_id ? "bold" : "normal"}>
                  {chat.name || `Chat ${chat.conversation_id.slice(0, 8)}`}
                </Text>
              </Box>
            ))
          )}
        </Box>
        {/* Pagination Controls */}
        <Flex justify="space-between" mt={4}>
          <Button
            size="sm"
            variant="outline"
            colorScheme="gray"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={!hasPrev}
          >
            Prev
          </Button>
          <Button
            size="sm"
            variant="outline"
            colorScheme="gray"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNext}
          >
            Next
          </Button>
        </Flex>
      </Box>
      {/* Main Chat Area */}
      <Box flex="1" bg={mainBg} p={0}>
        {children({ selectedChatId, onSelectChat: setSelectedChatId })}
      </Box>
    </Flex>
  )
} 