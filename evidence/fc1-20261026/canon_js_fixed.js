#!/usr/bin/env node
'use strict';
// Strict raw JSON parser: preserves duplicate detection before JSON.parse can overwrite keys.
// External canonicalization package required; absent => selftest fails and gate exits 2.
const fs = require('fs');
let canonicalize;
try { canonicalize = require('canonicalize').default; } catch (e) { console.error('PREREQ canonicalize missing'); process.exit(2); }
function strictParse(s) {
  let i=0;
  const ws=()=>{while(i<s.length && /[\t\r\n ]/.test(s[i]))i++};
  function str(){const st=i; if(s[i++]!=='"')throw Error('expected string');for(;;){if(i>=s.length)throw Error('truncated string');const c=s[i++];if(c==='"')break;if(c==='\\'){if(i>=s.length)throw Error('truncated escape');const e=s[i++];if(e==='u'){if(!/^[0-9a-fA-F]{4}$/.test(s.slice(i,i+4)))throw Error('invalid escape');i+=4;}else if(!'"\\/bfnrt'.includes(e))throw Error('invalid escape');}else if(c.charCodeAt(0)<32)throw Error('control character');}return JSON.parse(s.slice(st,i));}
  function value(){ws();const c=s[i];if(c==='"'){str();return}if(c==='{'){i++;ws();const seen=new Set();if(s[i]==='}'){i++;return}for(;;){ws();if(s[i]!=='"')throw Error('expected key');const k=str();if(seen.has(k))throw Error('duplicate key: '+k);seen.add(k);ws();if(s[i++]!==':')throw Error('expected colon');value();ws();if(s[i]==='}'){i++;break}if(s[i++]!==',')throw Error('expected comma')}return}if(c==='['){i++;ws();if(s[i]===']'){i++;return}for(;;){value();ws();if(s[i]===']'){i++;break}if(s[i++]!==',')throw Error('expected comma')}return}const tail=s.slice(i), m=/^(?:-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|true|false|null)/.exec(tail);if(!m)throw Error('invalid value');i+=m[0].length;}
  if(s.charCodeAt(0)===0xfeff)throw Error('BOM');value();ws();if(i!==s.length)throw Error('trailing data');return JSON.parse(s);
}
if(process.argv.includes('--selftest')) {try{if(strictParse('{"a":1,"a":2}')) process.exit(1)}catch(e){if(!String(e).includes('duplicate'))process.exit(1)}try{if(canonicalize({z:1,a:2})!=='{"a":2,"z":1}')process.exit(1)}catch(e){process.exit(1)}process.exit(0)}
const raw=fs.readFileSync(0);let s;try{s=new TextDecoder('utf-8',{fatal:true}).decode(raw);const v=strictParse(s);const out=canonicalize(v);if(typeof out!=='string')throw Error('canonicalizer failed');process.stdout.write(out)}catch(e){console.error(String(e));process.exit(1)}
