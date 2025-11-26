import { GitBranch, Construction } from 'lucide-react'
import Header from '@/components/layout/Header'

export default function GraphPage() {
  return (
    <>
      <Header title="Knowledge Graph" icon={<GitBranch className="w-5 h-5 text-gray-600" />} />

      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Construction className="w-8 h-8 text-gray-400" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Coming Soon</h2>
          <p className="text-gray-500">
            The Knowledge Graph feature will visualize connections between your memories,
            showing relationships between apps, topics, and activities over time.
          </p>
          <div className="mt-6 p-4 bg-gray-50 rounded-lg text-left">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Planned Features:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Interactive node visualization</li>
              <li>• Topic clustering and connections</li>
              <li>• Time-based relationship mapping</li>
              <li>• Entity extraction from OCR text</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}
