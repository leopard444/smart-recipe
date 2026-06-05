import apiClient from './client'
import type { ApiResponse } from '@/types/api'

export function uploadImage(file: File): Promise<ApiResponse<{ url: string }>> {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}

export function deleteImage(filename: string): Promise<ApiResponse<null>> {
  return apiClient.delete(`/upload/image/${filename}`).then(res => res.data)
}
