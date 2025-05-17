import { Flex } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import { type UserPublic, UsersService } from "@/client"
import Navbar from "@/components/Common/Navbar"
import Sidebar from "@/components/Common/Sidebar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  // Fetch the current user at the highest level
  // This will populate the ["currentUser"] query cache for all child components
  useQuery<UserPublic>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  })

  return (
    <Flex direction="column" h="100vh">
      <Navbar />
      <Flex flex="1" overflow="hidden">
        <Sidebar />
        <Flex flex="1" direction="column" p={4} overflowY="auto">
          <Outlet />
        </Flex>
      </Flex>
    </Flex>
  )
}

export default Layout
