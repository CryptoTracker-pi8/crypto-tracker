import { useEffect, useRef } from 'react'

interface IntersectionOptions {
  threshold?: number | number[]
  rootMargin?: string
}

export function useInfiniteScroll(
  callback: () => void,
  options: IntersectionOptions = {}
) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          callback()
        }
      },
      {
        threshold: options.threshold ?? 0.1,
        rootMargin: options.rootMargin ?? '100px',
      }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      observer.disconnect()
    }
  }, [callback])

  return ref
}
