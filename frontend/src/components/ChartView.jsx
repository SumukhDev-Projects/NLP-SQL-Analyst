import { useEffect, useRef } from 'react'

export default function ChartView({ chart }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!chart || !ref.current) return

    // Dynamically import Plotly to keep bundle reasonable
    import('plotly.js-dist-min').then(Plotly => {
      Plotly.newPlot(
        ref.current,
        chart.data,
        {
          ...chart.layout,
          autosize: true,
          responsive: true,
        },
        {
          displayModeBar: true,
          modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
          displaylogo: false,
          responsive: true,
        }
      )
    })

    return () => {
      import('plotly.js-dist-min').then(Plotly => {
        if (ref.current) Plotly.purge(ref.current)
      })
    }
  }, [chart])

  return (
    <div
      ref={ref}
      className="w-full rounded-lg overflow-hidden"
      style={{ minHeight: '360px' }}
    />
  )
}
