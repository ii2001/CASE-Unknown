import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'
import Investigation from './components/Investigation.vue'
import type { Game } from './types'

const game:Game={id:'case-1',title:'블랙아웃 프로토콜',genre:'sabotage',introduction:'intro',incident_summary:'incident',current_location_id:'lobby',visited_location_ids:['lobby'],unlocked_location_ids:['lobby'],narratives:['사건 시작'],completed:false,won:null,suspects:[{id:'yoon',name:'윤재호',role:'보안',public_profile:'관리자',portrait_url:'/p.svg'}],locations:[{id:'lobby',name:'유리 로비',description:'비 내리는 로비',locked:false,image_url:'/l.svg'}],evidence:[{id:'key',title:'출입 기록',category:'access',critical:true,description:'22:55 기록',image_url:'/e.svg'}],interviews:[],cover_url:'/c.svg'}

beforeEach(()=>{setActivePinia(createPinia());vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:()=>Promise.resolve({latest_case_id:null})}))})
describe('CASE UNKNOWN',()=>{
  it('renders landing and new case workflow',()=>{const w=mount(App,{global:{plugins:[createPinia()]}});expect(w.text()).toContain('CASE:');expect(w.text()).toContain('NEW CASE')})
  it('renders investigation, image, suspect and evidence board',async()=>{const w=mount(Investigation,{props:{game,loading:false,streamed:''}});expect(w.text()).toContain('유리 로비');expect(w.find('img[alt="유리 로비"]').exists()).toBe(true);expect(w.text()).toContain('출입 기록');await w.findAll('.board nav button')[1].trigger('click');expect(w.text()).toContain('윤재호')})
  it('emits actions and opens accusation modal',async()=>{const w=mount(Investigation,{props:{game,loading:false,streamed:''}});await w.find('#action').setValue('CCTV 확인');await w.find('form').trigger('submit');expect(w.emitted('act')?.[0]).toEqual(['CCTV 확인']);await w.find('.accuse').trigger('click');expect(w.text()).toContain('FINAL ACCUSATION')})
  it('shows streamed text',()=>{const w=mount(Investigation,{props:{game:{...game,narratives:['old']},loading:false,streamed:'스트리밍 중'}});expect(w.text()).toContain('스트리밍 중')})
})
