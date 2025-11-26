import { clsx } from 'clsx'

interface TagProps {
  label: string
  onClick?: () => void
  className?: string
}

export default function Tag({ label, onClick, className }: TagProps) {
  const isClickable = !!onClick

  return (
    <span
      onClick={onClick}
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border',
        'bg-white text-gray-700 border-gray-300',
        isClickable && 'cursor-pointer hover:bg-gray-50 hover:border-gray-400',
        className
      )}
    >
      {label}
    </span>
  )
}
