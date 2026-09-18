import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Game } from '../types'

export const useGameStore = defineStore('game', () => {
  const game = ref<Game|null>(null)
  const loading = ref(false)
  const error = ref('')
  const streamed = ref('')
  async function request<T>(url:string, options?:RequestInit):Promise<T> {
    const response = await fetch(url, { headers:{'Content-Type':'application/json'}, ...options })
    if (!response.ok) throw new Error((await response.json()).detail || '요청에 실패했습니다.')
    return response.json()
  }
  async function create(genre:string) { loading.value=true; error.value=''; try { game.value=await request('/api/cases',{method:'POST',body:JSON.stringify({genre,difficulty:'normal'})}) } catch(e){error.value=(e as Error).message} finally{loading.value=false} }
  async function load(id:string) { loading.value=true; try { game.value=await request(`/api/cases/${id}`) } finally { loading.value=false } }
  async function act(text:string) { if(!game.value||!text.trim()||loading.value)return; loading.value=true; streamed.value=''; try { const data=await request<{case:Game}>(`/api/cases/${game.value.id}/actions`,{method:'POST',body:JSON.stringify({text,request_id:crypto.randomUUID()})}); game.value=data.case; stream() } catch(e){error.value=(e as Error).message} finally{loading.value=false} }
  async function accuse(suspect_id:string, reasoning:string) { if(!game.value)return; loading.value=true; try { const data=await request<{case:Game}>(`/api/cases/${game.value.id}/accuse`,{method:'POST',body:JSON.stringify({suspect_id,reasoning})}); game.value=data.case; stream() } finally { loading.value=false } }
  function stream(){ if(!game.value)return; const source=new EventSource(`/api/cases/${game.value.id}/events/stream`); source.onmessage=e=>{streamed.value+=JSON.parse(e.data).chunk}; source.addEventListener('done',()=>source.close()); source.onerror=()=>source.close() }
  return { game,loading,error,streamed,create,load,act,accuse }
})
