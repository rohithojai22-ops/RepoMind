import {useEffect,useState} from "react";
import {Github,Send,Loader2,Database,Code2,Search} from "lucide-react";
import {ingestRepository,getRepositories,askQuestion} from "./api";

export default function App(){
 const [url,setUrl]=useState(""),[repos,setRepos]=useState([]),[selected,setSelected]=useState(null);
 const [question,setQuestion]=useState(""),[messages,setMessages]=useState([]),[loading,setLoading]=useState(false);
 const [ingesting,setIngesting]=useState(false),[error,setError]=useState("");

 async function loadRepos(){
   try{const data=await getRepositories();setRepos(data);if(!selected&&data.length)setSelected(data[0]);}
   catch{setError("Backend is not running or database is unavailable.");}
 }
 useEffect(()=>{loadRepos()},[]);

 async function handleIngest(e){
   e.preventDefault();if(!url.trim())return;setIngesting(true);setError("");
   try{
     const r=await ingestRepository(url.trim());
     setUrl("");await loadRepos();
     const fresh={id:r.repository_id,name:r.name,owner:r.owner,url:r.url||url,status:r.status};
     setSelected(fresh);setMessages([]);
   }catch(err){setError(err.response?.data?.detail||"Repository ingestion failed.");}
   finally{setIngesting(false)}
 }

 async function handleAsk(e){
   e.preventDefault();if(!question.trim()||!selected||loading)return;
   const q=question.trim();setQuestion("");setMessages(m=>[...m,{role:"user",text:q}]);setLoading(true);setError("");
   try{const r=await askQuestion(selected.id,q);setMessages(m=>[...m,{role:"assistant",text:r.answer,sources:r.sources}]);}
   catch(err){setError(err.response?.data?.detail||"Question failed.");}
   finally{setLoading(false)}
 }

 return <div className="app">
  <aside className="sidebar">
   <div className="brand"><div className="logo"><Code2 size={22}/></div><div><strong>RepoMind</strong><span>Codebase Intelligence</span></div></div>
   <div className="section-title">REPOSITORIES</div>
   <form onSubmit={handleIngest} className="ingest">
    <div className="input-wrap"><Github size={17}/><input value={url} onChange={e=>setUrl(e.target.value)} placeholder="GitHub repository URL"/></div>
    <button disabled={ingesting}>{ingesting?<Loader2 className="spin" size={17}/>:<Database size={17}/>} {ingesting?"Indexing...":"Index Repository"}</button>
   </form>
   <div className="repo-list">{repos.map(r=><button key={r.id} className={"repo "+(selected?.id===r.id?"active":"")} onClick={()=>{setSelected(r);setMessages([])}}><Github size={17}/><span><b>{r.name}</b><small>{r.owner} · {r.status}</small></span></button>)}{!repos.length&&<p className="muted">Index a GitHub repository to begin.</p>}</div>
  </aside>

  <main className="main">
   <header><div><div className="eyebrow">AI CODEBASE ASSISTANT</div><h1>{selected?`${selected.owner}/${selected.name}`:"RepoMind"}</h1><p>Ask questions using hybrid RAG and Gemini.</p></div><div className="pill"><Search size={15}/>BM25 + Vector + Reranker</div></header>
   {error&&<div className="error">{error}</div>}
   <section className="chat">
    {!selected?<div className="empty"><Code2 size={44}/><h2>Understand any codebase</h2><p>Paste a public GitHub repository URL on the left.</p></div>:
     messages.length===0?<div className="empty"><div className="hero-icon"><Code2 size={40}/></div><h2>Ask about {selected.name}</h2><p>Try one:</p><div className="suggestions">{["Explain the project architecture","Where is authentication implemented?","How does the frontend communicate with the backend?","Find the main database configuration"].map(x=><button key={x} onClick={()=>setQuestion(x)}>{x}</button>)}</div></div>:
     <div className="messages">{messages.map((m,i)=><div className={"message "+m.role} key={i}><div className="avatar">{m.role==="user"?"You":"RM"}</div><div className="bubble"><div className="text">{m.text}</div>{m.sources?.length>0&&<div className="sources"><strong>SOURCES</strong>{m.sources.map((s,j)=><div className="source" key={j}><Code2 size={14}/>{s.path}:{s.start_line}-{s.end_line}</div>)}</div>}</div></div>)}{loading&&<div className="message assistant"><div className="avatar">RM</div><div className="bubble typing"><Loader2 className="spin" size={18}/> Gemini is analyzing the code...</div></div>}</div>}
   </section>
   <form className="composer" onSubmit={handleAsk}><input value={question} onChange={e=>setQuestion(e.target.value)} disabled={!selected||loading} placeholder={selected?"Ask RepoMind about this codebase...":"Select a repository first"}/><button disabled={!selected||loading||!question.trim()}><Send size={18}/></button></form>
   <div className="footer">Gemini generates grounded answers from retrieved repository context.</div>
  </main>
 </div>
}
