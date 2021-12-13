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

export function titleCase(str: string) {
  return str.replace(
    /\w\S*/g,
    function(txt: string) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }
  );
}