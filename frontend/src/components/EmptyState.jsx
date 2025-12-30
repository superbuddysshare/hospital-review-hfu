import { ChatCircleDots } from '@phosphor-icons/react'
import { motion } from 'framer-motion'

export function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center py-16 px-4"
    >
      <motion.div
        animate={{ 
          y: [0, -10, 0],
        }}
        transition={{ 
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="mb-6 text-muted-foreground"
      >
        <ChatCircleDots size={80} weight="duotone" />
      </motion.div>
      <h3 className="text-2xl font-bold mb-2 text-foreground">No Reviews Yet</h3>
      <p className="text-muted-foreground text-center max-w-md mb-6">
        Be the first to share your hospital experience and help others make informed healthcare decisions.
      </p>
    </motion.div>
  )
}
