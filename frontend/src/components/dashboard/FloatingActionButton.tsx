import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X } from 'lucide-react';

interface Action {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  color: string;
}

interface FloatingActionButtonProps {
  actions: Action[];
}

/**
 * Floating action button with physics-based menu expansion
 * Provides quick access to common actions
 */
export default function FloatingActionButton({ actions }: FloatingActionButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-8 right-8 z-50">
      {/* Action menu items */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="absolute bottom-20 right-0 flex flex-col gap-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {actions.map((action, index) => (
              <motion.button
                key={index}
                onClick={() => {
                  action.onClick();
                  setIsOpen(false);
                }}
                className="group flex items-center gap-3"
                initial={{
                  opacity: 0,
                  x: 50,
                  scale: 0
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                  scale: 1
                }}
                exit={{
                  opacity: 0,
                  x: 50,
                  scale: 0
                }}
                transition={{
                  type: 'spring',
                  stiffness: 400,
                  damping: 25,
                  delay: index * 0.05
                }}
                whileHover={{ scale: 1.1, x: -5 }}
                whileTap={{ scale: 0.95 }}
              >
                {/* Label */}
                <motion.span
                  className="px-4 py-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-lg text-white text-sm font-medium whitespace-nowrap"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 + 0.1 }}
                >
                  {action.label}
                </motion.span>

                {/* Icon button */}
                <div
                  className={`w-12 h-12 rounded-full bg-gradient-to-br ${action.color} flex items-center justify-center text-white shadow-lg`}
                >
                  {action.icon}
                </div>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main FAB */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white shadow-2xl"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{
          rotate: isOpen ? 45 : 0
        }}
        transition={{
          type: 'spring',
          stiffness: 400,
          damping: 25
        }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X className="w-6 h-6" />
            </motion.div>
          ) : (
            <motion.div
              key="open"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Plus className="w-6 h-6" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Ripple effect */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500"
            initial={{ scale: 1, opacity: 0.5 }}
            animate={{
              scale: 2,
              opacity: 0
            }}
            exit={{ scale: 1, opacity: 0 }}
            transition={{ duration: 0.6 }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
