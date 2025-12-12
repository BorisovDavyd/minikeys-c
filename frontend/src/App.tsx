import React, { useState } from 'react'
import axios from 'axios'

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

type GeneratedFile = { path: string; content: string }

type Report = { passed?: boolean; failed?: boolean; issues?: any[]; duplicates?: any[]; recommendations?: string[]; test_plan?: string[] }

const tabs = [
  'Manual from UI',
  'Manual from OpenAPI',
  'Generate UI e2e',
  'Generate API tests',
  'Validate',
  'Optimize',
]

const defaultUI = `Landing page shows steps and add service button.`
const defaultOpenAPI = `Refer to sample_inputs/openapi_sample.yaml`

const FileViewer: React.FC<{ files: GeneratedFile[] }> = ({ files }) => (
  <div className="files">
    {files.map((f) => (
      <div key={f.path} className="file-item">
        <div className="file-path">{f.path}</div>
        <pre>{f.content}</pre>
      </div>
    ))}
  </div>
)

const ReportView: React.FC<{ report?: Report }> = ({ report }) => {
  if (!report) return null
  return (
    <div className="report">
      <pre>{JSON.stringify(report, null, 2)}</pre>
    </div>
  )
}

const App: React.FC = () => {
  const [active, setActive] = useState(tabs[0])
  const [text, setText] = useState(defaultUI)
  const [openapi, setOpenapi] = useState('')
  const [files, setFiles] = useState<GeneratedFile[]>([])
  const [report, setReport] = useState<Report>()

  const handleManualUI = async () => {
    const resp = await axios.post(`${backendUrl}/api/generate/manual`, { source_type: 'ui', text })
    setFiles(resp.data.files)
  }

  const handleManualAPI = async () => {
    const resp = await axios.post(`${backendUrl}/api/generate/manual`, { source_type: 'openapi', openapi_yaml: openapi })
    setFiles(resp.data.files)
  }

  const handleAutoUI = async () => {
    const resp = await axios.post(`${backendUrl}/api/generate/auto/ui`, { requirements_text: text })
    setFiles(resp.data.files)
  }

  const handleAutoAPI = async () => {
    const resp = await axios.post(`${backendUrl}/api/generate/auto/api`, { openapi_yaml: openapi, base_url: 'http://localhost' })
    setFiles(resp.data.files)
  }

  const handleValidate = async () => {
    const resp = await axios.post(`${backendUrl}/api/validate`, { manual_tests: files })
    setReport(resp.data.report)
  }

  const handleOptimize = async () => {
    const resp = await axios.post(`${backendUrl}/api/optimize`, { manual_tests: files, requirements_text: text, openapi_yaml: openapi })
    setReport(resp.data.report)
  }

  const renderTab = () => {
    switch (active) {
      case 'Manual from UI':
        return (
          <div>
            <textarea value={text} onChange={(e) => setText(e.target.value)} />
            <button onClick={handleManualUI}>Generate</button>
          </div>
        )
      case 'Manual from OpenAPI':
        return (
          <div>
            <textarea value={openapi} onChange={(e) => setOpenapi(e.target.value)} placeholder={defaultOpenAPI} />
            <button onClick={handleManualAPI}>Generate</button>
          </div>
        )
      case 'Generate UI e2e':
        return (
          <div>
            <textarea value={text} onChange={(e) => setText(e.target.value)} />
            <button onClick={handleAutoUI}>Generate</button>
          </div>
        )
      case 'Generate API tests':
        return (
          <div>
            <textarea value={openapi} onChange={(e) => setOpenapi(e.target.value)} placeholder={defaultOpenAPI} />
            <button onClick={handleAutoAPI}>Generate</button>
          </div>
        )
      case 'Validate':
        return <button onClick={handleValidate}>Validate Current Files</button>
      case 'Optimize':
        return <button onClick={handleOptimize}>Optimize</button>
      default:
        return null
    }
  }

  return (
    <div className="app">
      <h1>TestOps Copilot</h1>
      <div className="tabs">
        {tabs.map((tab) => (
          <button key={tab} className={tab === active ? 'active' : ''} onClick={() => setActive(tab)}>
            {tab}
          </button>
        ))}
      </div>
      <div className="panel">{renderTab()}</div>
      <FileViewer files={files} />
      <ReportView report={report} />
    </div>
  )
}

export default App
