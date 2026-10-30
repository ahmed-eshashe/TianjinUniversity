// Run only inside functions.exec, where the tools API is provided.
// Serial orchestration of unchanged guarded workers; no physical expressions.
const root = '/home/omen/teamwork_projects/tomato_cutting_right_arm';
const home = 'runs/offline/tomato_overnight_20261026';
const cohort = 'runs/offline/tomato_curvature_search_01';
async function shell(cmd) {
  const r = await tools.exec_command({cmd, workdir:root, max_output_tokens:60000});
  if (r.exit_code !== 0) throw Error(r.output);
  return r.output;
}
async function save(path, value) {
  await shell("python3 - <<'PY'\nfrom pathlib import Path\nPath(" + JSON.stringify(path) + ").write_text(" + JSON.stringify(JSON.stringify(value, null, 2)) + "+'\\n')\nPY");
}
async function quota() {
  const q = await tools.mcp__codex_app__get_usage_limits({});
  if (q.isError) throw Error('Quota unreadable');
  const d = JSON.parse(q.content.find(x => x.type === 'text').text);
  const windows = Object.values(d.rateLimitsByLimitId || {legacy:d.rateLimits}).flatMap(b => [b.primary,b.secondary]).filter(Boolean);
  if (!windows.length || windows.some(w => !Number.isFinite(w.usedPercent) || w.usedPercent >= 45)) throw Error('Quota stop');
  const utc = (await tools.clock__curr_time({})).current_time.replace(' UTC','').replace(' ','T') + '+00:00';
  const reading = {checked_utc:utc, maximum_reported_used_percent:Math.max(...windows.map(w=>w.usedPercent)), reported_windows:windows, secondary:'unknown'};
  await save(home+'/quota_lease.json',reading);
  return reading;
}
async function run(cmd) {
  let r = await tools.exec_command({cmd,workdir:root,yield_time_ms:1000,max_output_tokens:200});
  while (r.session_id) r = await tools.write_stdin({session_id:r.session_id,chars:'',yield_time_ms:30000,max_output_tokens:200});
  if (r.exit_code !== 0) throw Error('Guarded command exited '+r.exit_code);
}
const config = JSON.parse(await shell('cat '+home+'/session.json'));
let previous = config.last_accepted, target = config.target_mm, resume = config.pending_candidate;
let depth = JSON.parse(await shell("python3 - <<'PY'\nimport json\nfrom pathlib import Path\ns=json.loads(Path("+JSON.stringify(previous+'/summary.json')+").read_text());print(json.dumps({'depth':s['depth_mm']}))\nPY")).depth;
let step = target-depth;
if (!(step>0 && step<=.031250001)) throw Error('Invalid insertion interval');
let index = Number(await shell("python3 - <<'PY'\nfrom pathlib import Path\nimport re\na=[int(re.match(r'insertion(\\d+)',p.name).group(1)) for p in Path('"+cohort+"').glob('insertion*') if re.match(r'insertion(\\d+)',p.name)];print(max(a)+1)\nPY"));
const first = await quota(), sessionEnd = Date.parse(first.checked_utc)+8*60000;
const stamp = first.checked_utc.slice(11,16).replace(':','');
const prefix = 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 ';
for (let count=0; count<6; count++,index++) {
  const before=await quota();
  if (Date.parse(before.checked_utc)>=Math.min(sessionEnd-180000,Date.parse(config.final_scheduled_session_utc))) break;
  const name=`insertion${index}_20261026_h${stamp}`, batch=cohort+'/'+name;
  config.status='active';config.active_batch=batch;await save(home+'/session.json',config);
  await run(prefix+`.venv-native/bin/python ${config.runner} --name ${name} --previous ${previous} --depth-mm ${target} `+(resume?`--initial-resume ${resume}`:'--predict')+` > ${home}/insertion${index}.log`);
  let after=await quota();
  const status=JSON.parse(await shell('cat '+batch+'/status.json'));
  const event={batch,target_mm:target,step_mm:step,calls:status.calls,stop:status.stop_reason,accepted:status.accepted,checked_utc:after.checked_utc,used:after.maximum_reported_used_percent};
  let stop=false;
  if (status.accepted) {previous=status.accepted;depth=target;target=depth+step;resume=null;}
  else if (status.stop_reason==='physical_gate_failed') {
    const state=JSON.parse(await shell('cat '+status.records.at(-1).output+'/summary.json'));
    event.flags=state.flags;event.swept_gap_m=state.swept_blade_minimum_gap_m;
    stop=state.flags.some(f=>!['contact','incremental_work_balance','cumulative_work_balance'].includes(f));
    if (!stop) {step/=2;target=depth+step;resume=null;}
  } else if (['bounded_worker_budget','repeated_uncommitted_optimizer_state'].includes(status.stop_reason)) {
    resume=status.records.at(-1).output;
    if (status.stop_reason==='repeated_uncommitted_optimizer_state') {
      const now=await quota();
      if (Date.parse(now.checked_utc)<sessionEnd-90000) {
        const seed=`runs/offline/tomato_global_search_01/seed_h${stamp}_${index}`;
        await run(prefix+`timeout 60 .venv-native/bin/python ${config.seed_runner} --candidate ${resume} --previous ${previous} --output ${seed} --iterations 30 > ${home}/seed_h${stamp}_${index}.log`);
        after=await quota();resume=seed;event.seed=seed;event.checked_utc=after.checked_utc;event.used=after.maximum_reported_used_percent;
      }
    }
  } else stop=true;
  event.next_previous=previous;event.next_target=target;event.resume=resume;event.stop_required=stop;
  config.last_accepted=previous;config.target_mm=target;config.pending_candidate=resume;config.active_batch=null;config.last_quota_check_utc=event.checked_utc;config.last_reported_used_percent=event.used;
  config.status=stop?'needs_failure_review':'waiting_for_scheduled_continuation';
  config.next_experiment='Use the recorded accepted predecessor and exact target; resume pending candidate only at same target. Hold current step, halve contact/work failure, stop other physical failures.';
  await save(home+'/session.json',config);
  await shell("python3 - <<'PY'\nfrom pathlib import Path\ns="+JSON.stringify(JSON.stringify(event))+"\nfor p in ['"+home+"/heartbeat_"+stamp+".jsonl','docs/rl/OVERNIGHT_PROGRESS.md']:\n with Path(p).open('a') as f:f.write('\\n'+s+'\\n')\nPY");
  notify({batch,stop:event.stop,accepted:event.accepted,quota_used:event.used});
  if (stop) break;
}
text({last_accepted:previous,target_mm:target,pending_candidate:resume,step_mm:step});
