# Dark Mode Guidelines

## Overview

This project supports both light and dark modes. All UI components must be designed with both themes in mind to ensure a consistent user experience.

## Core Rules

1. **Never use hard-coded colors** for UI elements that would render differently in dark mode
   
2. **Always use `useColorModeValue`** from `@/components/ui/color-mode` for:
   - Background colors
   - Text colors
   - Border colors
   - Shadow effects
   
3. **For every UI component:**
   - Consider both light and dark appearances
   - Use the pattern: `const elementColor = useColorModeValue("light-value", "dark-value")`
   - Apply these values to all relevant style properties

## Common Color Pairs

Use these pre-defined color pairs for consistency:

| Element | Light Mode | Dark Mode | Usage Code |
|---------|------------|-----------|------------|
| Backgrounds | `white` | `gray.800` | `useColorModeValue("white", "gray.800")` |
| Borders | `gray.200` | `gray.700` | `useColorModeValue("gray.200", "gray.700")` |
| Subtle backgrounds | `gray.50` | `gray.900` | `useColorModeValue("gray.50", "gray.900")` |
| Text | `gray.800` | `white` | `useColorModeValue("gray.800", "white")` |
| Secondary text | `gray.600` | `gray.400` | `useColorModeValue("gray.600", "gray.400")` |
| Hover effects | `gray.100` | `gray.700` | `useColorModeValue("gray.100", "gray.700")` |

## Implementation Example

```tsx
import { Box, Text } from "@chakra-ui/react"
import { useColorModeValue } from "@/components/ui/color-mode"

function DarkModeAwareComponent() {
  // Define colors based on color mode
  const boxBg = useColorModeValue("white", "gray.800")
  const boxBorderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("gray.800", "white")

  return (
    <Box 
      p={4} 
      bg={boxBg} 
      borderColor={boxBorderColor} 
      borderWidth="1px" 
      borderRadius="md"
    >
      <Text color={textColor}>
        This component is dark mode compatible!
      </Text>
    </Box>
  )
}
```

## Checklist for New Components

When creating a new component or updating existing ones:

- [ ] Have you used `useColorModeValue` for all color properties?
- [ ] Have you tested the component in both light and dark modes?
- [ ] Are all text elements readable in both modes?
- [ ] Do interactive elements have appropriate hover/focus states in both modes?
- [ ] Are there any hard-coded color values that should be replaced?

## Import

Always import from our custom implementation:

```tsx
import { useColorModeValue } from "@/components/ui/color-mode"
```

Do NOT import from Chakra UI directly, as we use a custom implementation. 