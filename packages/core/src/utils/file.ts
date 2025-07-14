import { resolve, basename, dirname, extname } from 'path';
import { existsSync } from 'fs';

/**
 * Normalize file path for cross-platform compatibility
 * @param filePath File path to normalize
 * @returns Normalized file path
 */
export function normalizePath(filePath: string): string {
  return resolve(filePath).replace(/\\/g, '/');
}

/**
 * Extract filename from path
 * @param filePath Full file path
 * @returns Filename without extension
 */
export function getFileName(filePath: string): string {
  const name = basename(filePath);
  return name.substring(0, name.lastIndexOf('.')) || name;
}

/**
 * Get file extension
 * @param filePath File path
 * @returns File extension (with dot)
 */
export function getFileExtension(filePath: string): string {
  return extname(filePath);
}

/**
 * Get directory path
 * @param filePath File path
 * @returns Directory path
 */
export function getDirectoryPath(filePath: string): string {
  return dirname(filePath);
}

/**
 * Check if file exists
 * @param filePath Path to check
 * @returns True if file exists
 */
export function fileExists(filePath: string): boolean {
  return existsSync(filePath);
}

/**
 * Check if path is a JSONL file
 * @param filePath File path to check
 * @returns True if file has .jsonl extension
 */
export function isJsonlFile(filePath: string): boolean {
  return getFileExtension(filePath).toLowerCase() === '.jsonl';
}

/**
 * Sanitize filename for safe storage
 * @param filename Original filename
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string): string {
  return filename.replace(/[^a-zA-Z0-9._-]/g, '_');
}