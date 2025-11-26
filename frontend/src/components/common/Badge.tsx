import { clsx } from 'clsx'

interface BadgeProps {
  text: string
  variant?: 'default' | 'success' | 'warning' | 'info'
}

const variantStyles = {
  default: 'bg-gray-100 text-gray-600',
  success: 'bg-green-100 text-green-700',
  warning: 'bg-yellow-100 text-yellow-700',
  info: 'bg-blue-100 text-blue-700',
}

export default function Badge({ text, variant = 'default' }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
        variantStyles[variant]
      )}
    >
      {text}
    </span>
  )
}
