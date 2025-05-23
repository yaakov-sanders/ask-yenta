import { Box, HStack, Button, Text, IconButton, VStack } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { useColorModeValue, useColorMode } from "../ui/color-mode"
import * as React from "react"
import { FiUser } from "react-icons/fi"
import { LuMoon, LuSun } from "react-icons/lu"
import useAuth from "../../hooks/useAuth"

function ThemeMenuItem({ onClick }: { onClick: () => void }) {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <Button
      onClick={() => { toggleColorMode(); onClick(); }}
      variant="ghost"
      justifyContent="flex-start"
    >
      <Box as="span" mr={2} display="inline-flex" alignItems="center">
        {colorMode === "dark" ? <LuMoon /> : <LuSun />}
      </Box>
      Toggle Theme
    </Button>
  );
}

export function Navigation() {
  const bgColor = useColorModeValue("white", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")
  const { logout } = useAuth()
  const [menuOpen, setMenuOpen] = React.useState(false)
  const menuRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false)
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    } else {
      document.removeEventListener("mousedown", handleClickOutside)
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [menuOpen])

  return (
    <Box
      as="nav"
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      py={4}
      px={8}
    >
      <HStack gap={8} justify="space-between">
        <HStack gap={4}>
          <Link to="/chat" style={{ textDecoration: "none" }}>
            <Button colorScheme="blue" variant="solid">
              Chat
            </Button>
          </Link>
          <Link to="/connections" style={{ textDecoration: "none" }}>
            <Button colorScheme="blue" variant="solid">
              Connections
            </Button>
          </Link>
        </HStack>
        <Box position="relative" ref={menuRef}>
          <IconButton
            aria-label="User menu"
            variant="ghost"
            color={textColor}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <FiUser />
          </IconButton>
          {menuOpen && (
            <Box
              position="absolute"
              right={0}
              mt={2}
              bg={bgColor}
              border="1px solid"
              borderColor={borderColor}
              borderRadius="md"
              boxShadow="md"
              zIndex={10}
              minW="160px"
              p={2}
            >
              <VStack align="stretch" gap={2}>
                <ThemeMenuItem onClick={() => setMenuOpen(false)} />
                <Button onClick={() => { setMenuOpen(false); logout(); }} variant="ghost" justifyContent="flex-start">
                  Logout
                </Button>
              </VStack>
            </Box>
          )}
        </Box>
      </HStack>
    </Box>
  )
} 