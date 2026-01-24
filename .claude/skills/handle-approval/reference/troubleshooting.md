# Troubleshooting Guide

Common issues and solutions for the handle-approval skill.

**Last Updated:** 2026-01-11

---

## Common Issues

### Issue 1: Approval File Created But Action Not Executing

**Symptoms:**
- File exists in Vault/Pending_Approval
- Approval script shows it as pending
- Action never executes

**Causes:**
- File is still in Vault/Pending_Approval (not moved to Vault/Approved)
- File was moved to wrong folder
- File permissions issue

**Solution:**
1. Verify file is in Vault/Approved folder (not Vault/Pending_Approval)
2. Check file hasn't been accidentally moved to Vault/Rejected
3. Ensure filename hasn't changed during move
4. Check file permissions are readable

**Prevention:**
- Always move the entire file, don't copy
- Use file manager or git to move files
- Don't rename files when moving

---

### Issue 2: Execution Fails with "MCP Server Not Found"

**Symptoms:**
- Approval is in Vault/Approved folder
- Error message mentions MCP server
- Action fails to execute

**Causes:**
- MCP server not configured
- MCP server not running
- MCP server authentication failed
- Wrong MCP server name in configuration

**Solution:**
1. Check MCP server configuration in `~/.config/claude-code/mcp.json`
2. Verify MCP server process is running: `ps aux | grep mcp`
3. Test MCP server connection manually
4. Check MCP server logs for authentication errors
5. Restart MCP server if needed

**Prevention:**
- Test MCP servers during setup
- Monitor MCP server health
- Keep MCP server credentials updated

---

### Issue 3: Approval Marked as Expired Prematurely

**Symptoms:**
- Approval shows as expired
- Less than expiration time has passed
- Moved to Vault/Rejected with "EXPIRED" note

**Causes:**
- Timezone mismatch (UTC vs local time)
- System clock incorrect
- Expiration timestamp format incorrect
- Script timezone settings wrong

**Solution:**
1. Check system timezone: `date +%Z`
2. Verify expiration timestamp is in ISO 8601 format with Z suffix
3. Check check_approval_status.py timezone handling
4. Ensure all timestamps use UTC (not local time)

**Prevention:**
- Always use UTC timestamps (ISO 8601 with Z suffix)
- Don't manually edit timestamps
- Use consistent timezone across all systems

---

### Issue 4: Can't Find Pending Approvals

**Symptoms:**
- User claims they created approval
- check_approval_status.py shows 0 pending
- Approvals seem to disappear

**Causes:**
- File not in Vault/Pending_Approval folder
- Filename doesn't match APPROVAL_*.md pattern
- File was moved/deleted accidentally
- Working in wrong vault directory

**Solution:**
1. Verify current working directory: `pwd`
2. List files manually: `ls -la Vault/Pending_Approval/`
3. Check if file matches naming pattern: `APPROVAL_[TYPE]_[DESC]_[DATE].md`
4. Search entire vault: `find . -name "APPROVAL_*.md"`
5. Check git history if file was deleted

**Prevention:**
- Always use standard filename format
- Don't manually rename approval files
- Use handle-approval skill to create approvals (not manual creation)

---

### Issue 5: Approval File Has Invalid Format

**Symptoms:**
- Parsing errors when reading approval
- Missing required fields
- Execution fails with "Invalid approval format"

**Causes:**
- YAML frontmatter missing or malformed
- Required sections omitted
- Incorrect markdown syntax
- File corrupted during edit

**Solution:**
1. Verify YAML frontmatter starts with `---` and ends with `---`
2. Check all required fields present: type, action, created, expires, priority, status
3. Compare to [approval-template.md](./approval-template.md)
4. Use YAML validator if needed
5. Recreate approval file if corrupted

**Prevention:**
- Always use approval-template.md
- Don't manually edit YAML frontmatter
- Let handle-approval skill create approval files

---

### Issue 6: Script Encoding Errors (Windows)

**Symptoms:**
- UnicodeEncodeError when running check_approval_status.py
- Emoji characters not displaying
- Output truncated or garbled

**Causes:**
- Windows command prompt uses cp1252 encoding (not UTF-8)
- Emoji characters in script output
- Python default encoding mismatch

**Solution:**
1. Use `--json` flag: `python check_approval_status.py --json`
2. Set environment variable: `set PYTHONIOENCODING=utf-8`
3. Use PowerShell instead of cmd.exe
4. Use Windows Terminal (supports UTF-8 natively)

**Prevention:**
- Always use `--json` flag on Windows for programmatic parsing
- Configure Windows Terminal for UTF-8 support

---

### Issue 7: Duplicate Approvals Created

**Symptoms:**
- Multiple approval files for same action
- Confusion about which to approve
- Same action appears multiple times in pending list

**Causes:**
- Skill triggered multiple times
- User manually created duplicate
- Error in skill logic didn't check for existing approvals

**Solution:**
1. List all approvals: `ls -la Vault/Pending_Approval/APPROVAL_*`
2. Identify duplicates (same action, similar timestamps)
3. Keep most recent approval file
4. Move older duplicates to Vault/Rejected with note "DUPLICATE"

**Prevention:**
- Check for existing approval before creating new one
- Use unique filenames with timestamps
- Implement duplicate detection in skill logic

---

### Issue 8: Approval Executes Wrong Action

**Symptoms:**
- Action executes but does wrong thing
- Parameters don't match what was approved
- Unintended recipient or target

**Causes:**
- Parameters modified after approval creation
- File edited incorrectly
- Execution read wrong parameters
- Race condition (file changed during execution)

**Solution:**
1. STOP immediately - don't let action complete if possible
2. Check Execution Log section of approval file
3. Compare original parameters to executed parameters
4. Review Vault/Dashboard.md for what actually happened
5. If sent incorrectly, send correction/apology immediately

**Prevention:**
- Never modify approval files in Vault/Approved folder
- If changes needed, reject and create new approval
- Implement parameter validation before execution
- Log all parameter values before execution

---

### Issue 9: Approval Script Hangs or Crashes

**Symptoms:**
- check_approval_status.py doesn't complete
- Script hangs indefinitely
- Process uses 100% CPU

**Causes:**
- Large number of approval files (>1000)
- Corrupted approval file causing parsing loop
- File permission issue
- Disk I/O problem

**Solution:**
1. Kill script: `Ctrl+C` or `pkill -f check_approval_status`
2. Check approval file count: `ls -1 Vault/Pending_Approval/ | wc -l`
3. Find problematic file: Test files individually
4. Move problematic files aside temporarily
5. Run script with `--json` flag (faster parsing)

**Prevention:**
- Archive old approvals regularly (move completed to Vault/Done)
- Limit approval folder size (<100 files)
- Implement file count warning in script

---

### Issue 10: Permission Denied Errors

**Symptoms:**
- Can't read approval files
- Can't move files between folders
- Can't execute check_approval_status.py

**Causes:**
- File ownership mismatch
- Incorrect folder permissions
- Running as wrong user
- Vault on network drive with restrictions

**Solution:**
1. Check file ownership: `ls -l Vault/Pending_Approval/`
2. Fix permissions: `chmod 644 Vault/Pending_Approval/*.md`
3. Fix folder permissions: `chmod 755 Vault/Pending_Approval/`
4. Verify running as correct user: `whoami`
5. If on network drive, move vault to local disk

**Prevention:**
- Keep vault on local disk
- Don't mix sudo/normal user for vault operations
- Set proper permissions during vault setup

---

## Debugging Workflow

### Step 1: Gather Information
```bash
# Check approval folder contents
ls -la Vault/Pending_Approval/ Vault/Approved/ Vault/Rejected/

# Run status script with JSON output
python .claude/skills/handle-approval/scripts/check_approval_status.py --json

# Check Dashboard for recent activity
tail -20 Vault/Dashboard.md

# Check git status
git status
```

### Step 2: Verify File Format
```bash
# Read approval file
cat Vault/Pending_Approval/APPROVAL_*.md

# Check YAML frontmatter
head -10 Vault/Pending_Approval/APPROVAL_*.md

# Verify filename pattern
basename Vault/Pending_Approval/APPROVAL_*.md
```

### Step 3: Test Execution Path
```bash
# Move test approval to Approved
cp Vault/Pending_Approval/APPROVAL_TEST.md Vault/Approved/

# Try to process it (dry-run)
# [Use skill in dry-run mode if available]

# Check logs
tail -f Vault/Dashboard.md
```

### Step 4: Check External Dependencies
```bash
# Verify MCP servers
ps aux | grep mcp

# Test MCP server connection
# [MCP-specific testing command]

# Check API credentials
# [Verify credentials are valid]
```

---

## Error Messages Reference

### "Approval file not found"
- File was moved or deleted
- Working in wrong directory
- Filename typo

### "Invalid YAML frontmatter"
- Missing `---` delimiters
- Syntax error in YAML
- Required field missing

### "Approval expired"
- Current time > expires timestamp
- Normal behavior, not an error
- Can recreate if still needed

### "MCP server unavailable"
- Server not running
- Connection failed
- Authentication error

### "Parameter validation failed"
- Required parameter missing
- Parameter type incorrect
- Value out of range or invalid

### "Action not supported"
- Action type not recognized
- MCP server for action type not configured
- Typo in action field

---

## When to Ask for Help

If you've tried troubleshooting and still have issues:

1. **Gather diagnostic information:**
   - Error messages (full text)
   - Approval file content
   - check_approval_status.py output
   - Vault/Dashboard.md recent entries
   - System environment (OS, Python version)

2. **Document what you tried:**
   - Steps taken to resolve
   - Results of each attempt
   - Changes made

3. **Ask in Wednesday research meeting:**
   - Zoom: Wednesday 10 PM
   - Have diagnostic info ready
   - Be specific about the issue

---

## Preventive Maintenance

### Daily:
- Check pending approvals don't exceed 10
- Verify no expired approvals stuck in Vault/Pending_Approval
- Ensure Vault/Done folder isn't growing too large (archive monthly)

### Weekly:
- Review approval patterns (are too many being rejected?)
- Check MCP server health
- Verify API credentials haven't expired
- Archive completed approvals from Vault/Done to yearly folder

### Monthly:
- Review approval-thresholds.md (adjust if needed)
- Update security-rules.md based on lessons learned
- Test all MCP server connections
- Clean up old test approvals

---

*Following this guide helps resolve most approval workflow issues quickly.*

*Last Updated: 2026-01-11*
*Version: 1.1 (Updated for Vault structure)*