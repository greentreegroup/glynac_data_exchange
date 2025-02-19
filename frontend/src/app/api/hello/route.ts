// app/api/hello/route.ts
export async function GET(request: Request,){
    const data = {message: "hello node.js API !"};
    return new Response(JSON.stringify(data),{
        status: 200,
        headers:{"content-type":"application/json"},
    });

}