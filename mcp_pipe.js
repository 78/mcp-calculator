#!/usr/bin/env node
/**
 * MCP stdio <-> WebSocket pipe (Node.js version)
 * Usage: node mcp_pipe.js
 * Requires: npm install ws
 */

const WebSocket = require('ws');
const { spawn } = require('child_process');

const MCP_ENDPOINT = process.env.MCP_ENDPOINT;
if (!MCP_ENDPOINT) {
    console.error('Please set MCP_ENDPOINT environment variable');
    process.exit(1);
}

const config = require('./mcp_config.json');
const servers = config.mcpServers || {};

// 过滤启用的服务器
const enabledServers = Object.entries(servers)
    .filter(([name, cfg]) => !cfg?.disabled)
    .map(([name]) => name);

const disabledServers = Object.entries(servers)
    .filter(([name, cfg]) => cfg?.disabled)
    .map(([name]) => name);

if (disabledServers.length > 0) {
    console.log(`Skipping disabled servers: ${disabledServers.join(', ')}`);
}

if (enabledServers.length === 0) {
    console.error('No enabled mcpServers found in config');
    process.exit(1);
}

console.log(`Starting servers: ${enabledServers.join(', ')}`);

function connectServer(target) {
    const serverCfg = servers[target];
    if (!serverCfg) {
        console.error(`[${target}] Server not found in config`);
        return;
    }

    const ws = new WebSocket(MCP_ENDPOINT);
    let childProcess = null;

    ws.on('open', () => {
        console.log(`[${target}] WebSocket connected`);

        // 启动本地进程
        const cmd = serverCfg.command || 'python';
        const args = serverCfg.args || [];
        const env = { ...process.env, ...(serverCfg.env || {}) };

        childProcess = spawn(cmd, args, {
            stdio: ['pipe', 'pipe', 'pipe'],
            env
        });

        console.log(`[${target}] Started process: ${cmd} ${args.join(' ')}`);

        // WebSocket -> Process stdin
        ws.on('message', (data) => {
            if (childProcess && !childProcess.killed) {
                childProcess.stdin.write(data + '\n');
            }
        });

        // Process stdout -> WebSocket
        childProcess.stdout.on('data', (data) => {
            const lines = data.toString().trim().split('\n');
            lines.forEach(line => {
                if (line) ws.send(line);
            });
        });

        // Process stderr -> Terminal
        childProcess.stderr.on('data', (data) => {
            process.stderr.write(data);
        });

        childProcess.on('close', (code) => {
            console.log(`[${target}] Process exited with code ${code}`);
            ws.close();
        });
    });

    ws.on('message', (data) => {
        // 已在 open 中处理
    });

    ws.on('error', (err) => {
        console.error(`[${target}] WebSocket error: ${err.message}`);
    });

    ws.on('close', () => {
        console.log(`[${target}] WebSocket closed, reconnecting in 2s...`);
        if (childProcess && !childProcess.killed) {
            childProcess.kill();
        }
        setTimeout(() => connectServer(target), 2000);
    });
}

// 启动所有服务器
enabledServers.forEach(connectServer);

process.on('SIGINT', () => {
    console.log('\nShutting down...');
    process.exit(0);
});
