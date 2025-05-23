import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Box, VStack, HStack, Button, Text, Input, Spinner } from "@chakra-ui/react"
import { ConnectionsService, UsersService, UsersChatService } from "../client"
import { useState, useMemo } from "react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useColorModeValue } from "@/components/ui/color-mode"
import type { ConnectionPublic, UserPublic } from "../client/types.gen"

export const Route = createFileRoute('/connections')({
  component: ConnectionsPage,
})

function ConnectionsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // Get current user
  const { data: currentUser, isLoading: userLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
  })

  // Get all connections
  const { data: connections } = useQuery({
    queryKey: ["connections"],
    queryFn: () => ConnectionsService.readConnections(),
  })

  // Get all users (for mapping IDs to emails)
  const { data: allUsers } = useQuery({
    queryKey: ["allUsers"],
    queryFn: () => UsersService.readUsers(),
  })

  // Map userId to user info
  const userMap = useMemo(() => {
    const map: Record<string, UserPublic> = {}
    allUsers?.data.forEach((u) => { map[u.id] = u })
    if (currentUser) map[currentUser.id] = currentUser
    return map
  }, [allUsers, currentUser])

  // Search users
  const { data: users } = useQuery({
    queryKey: ["users", searchQuery],
    queryFn: () => UsersService.readUsers(),
    enabled: searchQuery.length > 0,
  })

  // Create connection
  const createConnectionMutation = useMutation({
    mutationFn: (userId: string) =>
      ConnectionsService.createConnection({
        requestBody: { target_user_id: userId },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
  })

  // Accept connection
  const acceptConnectionMutation = useMutation({
    mutationFn: (connectionId: string) =>
      ConnectionsService.updateConnection({
        connectionId,
        requestBody: { status: "accepted" },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
  })

  // Create chat
  const createChatMutation = useMutation({
    mutationFn: (participantId: string) =>
      UsersChatService.createChat({
        requestBody: { participant_ids: [participantId] },
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["userChats"] })
      navigate({ to: '/user-chat', search: { chatId: data.conversation_id } })
    },
  })

  // Colors
  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const inputBg = useColorModeValue("gray.50", "gray.900")

  if (userLoading) return <Spinner />

  return (
    <Box p={4} maxW="container.md" mx="auto">
      <VStack gap={4} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" color={textColor}>
          Connections
        </Text>

        {/* Search Users */}
        <Box>
          <Text mb={2} color={textColor}>Find Users</Text>
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search users..."
            bg={inputBg}
            color={textColor}
          />
          {users?.data && (
            <VStack mt={2} gap={2} align="stretch">
              {users.data.map((user: UserPublic) => (
                <HStack
                  key={user.id}
                  p={2}
                  bg={bgColor}
                  borderColor={borderColor}
                  borderWidth="1px"
                  borderRadius="md"
                  justify="space-between"
                >
                  <Text color={textColor}>{user.email}</Text>
                  <Button
                    size="sm"
                    colorScheme="blue"
                    onClick={() => createConnectionMutation.mutate(user.id)}
                    loading={createConnectionMutation.isPending}
                  >
                    Connect
                  </Button>
                </HStack>
              ))}
            </VStack>
          )}
        </Box>

        {/* Connection Requests */}
        <Box>
          <Text mb={2} color={textColor}>Connection Requests</Text>
          <VStack gap={2} align="stretch">
            {connections?.data
              .filter((conn: ConnectionPublic) => conn.status === "pending")
              .map((conn: ConnectionPublic) => {
                const isTarget = conn.target_user_id === currentUser?.id
                const isSource = conn.source_user_id === currentUser?.id
                const otherUserId = isTarget ? conn.source_user_id : conn.target_user_id
                const otherUser = userMap[otherUserId]
                return (
                  <HStack
                    key={conn.id}
                    p={2}
                    bg={bgColor}
                    borderColor={borderColor}
                    borderWidth="1px"
                    borderRadius="md"
                    justify="space-between"
                  >
                    <Text color={textColor}>{otherUser?.email || otherUserId}</Text>
                    {isTarget ? (
                      <Button
                        size="sm"
                        colorScheme="green"
                        onClick={() => acceptConnectionMutation.mutate(conn.id)}
                        loading={acceptConnectionMutation.isPending}
                      >
                        Accept
                      </Button>
                    ) : isSource ? (
                      <Text color={textColor} fontSize="sm">Pending</Text>
                    ) : null}
                  </HStack>
                )
              })}
          </VStack>
        </Box>

        {/* Active Connections */}
        <Box>
          <Text mb={2} color={textColor}>Active Connections</Text>
          <VStack gap={2} align="stretch">
            {connections?.data
              .filter((conn: ConnectionPublic) => conn.status === "accepted")
              .map((conn: ConnectionPublic) => {
                const isTarget = conn.target_user_id === currentUser?.id
                const isSource = conn.source_user_id === currentUser?.id
                const otherUserId = isTarget ? conn.source_user_id : conn.target_user_id
                const otherUser = userMap[otherUserId]
                return (
                  <HStack
                    key={conn.id}
                    p={2}
                    bg={bgColor}
                    borderColor={borderColor}
                    borderWidth="1px"
                    borderRadius="md"
                    justify="space-between"
                  >
                    <Text color={textColor}>{otherUser?.email || otherUserId}</Text>
                    <Button
                      size="sm"
                      colorScheme="blue"
                      onClick={() => createChatMutation.mutate(otherUserId)}
                      loading={createChatMutation.isPending}
                    >
                      Chat
                    </Button>
                  </HStack>
                )
              })}
          </VStack>
        </Box>
      </VStack>
    </Box>
  )
} 