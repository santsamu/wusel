// Development-only export tool. The original selected artwork stays unchanged.
'use strict';
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),assets=path.join(root,'wusel/static');
const option=process.argv.indexOf('--sharp-module');
const sharp=require(option>=0?path.resolve(process.argv[option+1]):'sharp');
async function main(){
 const source=fs.readFileSync(path.join(assets,'wusel-logo.png'));
 const {data,info}=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 let left=info.width,top=info.height,right=-1,bottom=-1;
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)if(data[(y*info.width+x)*4+3]>8){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}
 if(right<left)throw Error('The selected logo has no visible pixels');
 const mark=await sharp(source).extract({left,top,width:right-left+1,height:bottom-top+1}).png().toBuffer();
 await sharp(mark).resize({width:256}).png({compressionLevel:9}).toFile(path.join(assets,'wusel-mark.png'));
 await sharp(mark).resize({width:500}).png({compressionLevel:9}).toFile(path.join(root,'wusel/logo.png'));
 const background={r:255,g:249,b:238,alpha:1};
 async function tile(size){
  const foreground=await sharp(mark).resize({width:Math.round(size*.86),height:Math.round(size*.86),fit:'inside'}).png().toBuffer();
  return sharp({create:{width:size,height:size,channels:4,background}}).composite([{input:foreground,gravity:'centre'}]).png({compressionLevel:9}).toBuffer();
 }
 for(const size of [16,32,192,512])fs.writeFileSync(path.join(assets,'favicon-'+size+'.png'),await tile(size));
 fs.writeFileSync(path.join(assets,'apple-touch-icon.png'),await tile(180));
 fs.writeFileSync(path.join(root,'wusel/icon.png'),await tile(128));
 // ICO can contain standard PNG images; provide multiple sizes for browser/OS selection.
 const sizes=[16,32,48,64,128,256],images=await Promise.all(sizes.map(tile));
 const header=Buffer.alloc(6+16*sizes.length);header.writeUInt16LE(1,2);header.writeUInt16LE(sizes.length,4);
 let offset=header.length;
 sizes.forEach((size,index)=>{const at=6+16*index;header[at]=size===256?0:size;header[at+1]=header[at];header.writeUInt16LE(1,at+4);header.writeUInt16LE(32,at+6);header.writeUInt32LE(images[index].length,at+8);header.writeUInt32LE(offset,at+12);offset+=images[index].length;});
 fs.writeFileSync(path.join(assets,'favicon.ico'),Buffer.concat([header,...images]));
 console.log('Exported Wusel header mark, PNG/ICO favicons, Apple touch icon and Home Assistant icon/logo.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
