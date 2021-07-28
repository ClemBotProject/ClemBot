export function chunkArray<T extends any>(
  value: Array<T>,
  size: number
): Array<Array<T>> {
  const chunks: Array<Array<T>> = []

  let currentChunk: Array<T> = []

  for (const item of value) {
    if (currentChunk.length >= size) {
      chunks.push(currentChunk)
      currentChunk = []
    }

    currentChunk.push(item)
  }

  chunks.push(currentChunk)
  return chunks
}
