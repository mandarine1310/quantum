local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Camera = workspace.CurrentCamera
local LocalPlayer = Players.LocalPlayer
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local repo = "https://raw.githubusercontent.com/deividcomsono/Obsidian/main/"
local Library = loadstring(game:HttpGet(repo .. "Library.lua"))()
local ThemeManager = loadstring(game:HttpGet(repo .. "addons/ThemeManager.lua"))()
local SaveManager = loadstring(game:HttpGet(repo .. "addons/SaveManager.lua"))()

local Options = Library.Options
local Toggles = Library.Toggles

Library.ForceCheckbox = false
Library.ShowToggleFrameInKeybinds = true

local IsMobile = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled

local Window = Library:CreateWindow({ Title = ".gg/crystalized", Footer = "version: 1.0", Icon = 1234, NotifySide = "Right", ShowCustomCursor = true })

local Tabs = {
    Fighting = Window:AddTab("Fighting", "crosshair"),
    RageBot = Window:AddTab("RageBot", "zap"),
    ESP = Window:AddTab("ESP", "eye"),
    Player = Window:AddTab("Player", "user"),
    World = Window:AddTab("World + UI", "globe"),
    Crosshair = Window:AddTab("Crosshair", "aperture"),
    Spoof = Window:AddTab("Spoof", "shield"),
    ["UI Settings"] = Window:AddTab("UI Settings", "settings"),
}

local LeftGroupBox = Tabs.ESP:AddLeftGroupbox("ESP Toggles")
local RightGroupBox = Tabs.ESP:AddRightGroupbox("ESP Settings")

local PS = { SpeedEnabled = false, JumpEnabled = false, NoclipEnabled = false, InfiniteJump = false }
local hooks = { walkspeed = 16, jumppower = 50 }
local OrigWS, OrigJP = 16, 50

local function getHum() local char = LocalPlayer.Character; return char and char:FindFirstChildOfClass("Humanoid") end
local function rawSetWalkSpeed(v) local hum = getHum(); if hum then pcall(function() hum.WalkSpeed = v end) end end
local function rawSetJumpPower(v) local hum = getHum(); if hum then pcall(function() hum.JumpPower = v end) end end

local function captureOrig()
    local hum = getHum(); if not hum then return end
    if not PS.SpeedEnabled then pcall(function() OrigWS = hum.WalkSpeed end) end
    if not PS.JumpEnabled then pcall(function() OrigJP = hum.JumpPower end) end
end

local lastEnforce = 0
RunService.Heartbeat:Connect(function()
    local now = tick()
    if now - lastEnforce < 0.016 then return end
    lastEnforce = now
    local hum = getHum(); if not hum then return end
    if PS.SpeedEnabled then pcall(function() if math.abs(hum.WalkSpeed - hooks.walkspeed) > 0.01 then hum.WalkSpeed = hooks.walkspeed end end) end
    if PS.JumpEnabled then pcall(function() if math.abs(hum.JumpPower - hooks.jumppower) > 0.01 then hum.JumpPower = hooks.jumppower end end) end
end)

local noclipParts = {}
local function rebuildNoclip()
    noclipParts = {}
    local char = LocalPlayer.Character; if not char then return end
    for _, p in ipairs(char:GetDescendants()) do if p:IsA("BasePart") then noclipParts[#noclipParts + 1] = p end end
end
local function setCollision(state)
    for i = 1, #noclipParts do local p = noclipParts[i]; if p and p.Parent then pcall(function() p.CanCollide = state end) end end
end

UserInputService.JumpRequest:Connect(function()
    if not PS.InfiniteJump then return end
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    if hum then hum:ChangeState(Enum.HumanoidStateType.Jumping) end
end)

local function applyPS()
    local hum = getHum(); if not hum then return end
    captureOrig()
    if PS.SpeedEnabled then pcall(function() hum.WalkSpeed = hooks.walkspeed end) end
    if PS.JumpEnabled then pcall(function() hum.JumpPower = hooks.jumppower end) end
    rebuildNoclip()
end

LocalPlayer.CharacterAdded:Connect(function() task.wait(0.5); applyPS() end)
if LocalPlayer.Character then task.spawn(captureOrig); task.spawn(rebuildNoclip) end

local SlideBoost = { Enabled = false, Multiplier = 2 }
local slideConns = {}

local function boostBV(bv)
    if not bv:IsA("BodyVelocity") then return end
    local busy = false
    local function apply()
        if busy or not SlideBoost.Enabled then return end
        busy = true
        local v = bv.Velocity
        bv.Velocity = Vector3.new(v.X * SlideBoost.Multiplier, v.Y, v.Z * SlideBoost.Multiplier)
        busy = false
    end
    apply()
    table.insert(slideConns, bv:GetPropertyChangedSignal("Velocity"):Connect(apply))
end

local function setupSlide(char)
    for _, c in ipairs(slideConns) do c:Disconnect() end
    slideConns = {}
    local hrp = char:WaitForChild("HumanoidRootPart")
    for _, ch in ipairs(hrp:GetChildren()) do boostBV(ch) end
    table.insert(slideConns, hrp.ChildAdded:Connect(boostBV))
end

LocalPlayer.CharacterAdded:Connect(function(c) task.wait(0.5); setupSlide(c) end)
if LocalPlayer.Character then task.spawn(function() setupSlide(LocalPlayer.Character) end) end

local FlySettings = { Enabled = false, Speed = 50 }
local flyBV = Instance.new("BodyVelocity")
local flyBG = Instance.new("BodyGyro")
flyBV.MaxForce = Vector3.new(math.huge, math.huge, math.huge)
flyBG.MaxTorque = Vector3.new(math.huge, math.huge, math.huge)
flyBG.D = 100; flyBG.P = 10000

local flyKeys, flyConns = {}, {}

local function enableFly()
    local char = LocalPlayer.Character; if not char then return end
    local hrp = char:FindFirstChild("HumanoidRootPart"); if not hrp then return end
    local hum = char:FindFirstChildOfClass("Humanoid")
    if hum then hum:ChangeState(Enum.HumanoidStateType.Physics) end
    flyBV.Velocity = Vector3.zero; flyBV.Parent = hrp
    flyBG.CFrame = hrp.CFrame; flyBG.Parent = hrp
    flyKeys = {}
    for _, c in pairs(flyConns) do c:Disconnect() end; flyConns = {}
    flyConns[1] = UserInputService.InputBegan:Connect(function(i, g) if not g then flyKeys[i.KeyCode] = true end end)
    flyConns[2] = UserInputService.InputEnded:Connect(function(i) flyKeys[i.KeyCode] = nil end)
    flyConns[3] = RunService.RenderStepped:Connect(function(dt)
        if not FlySettings.Enabled then return end
        local r = LocalPlayer.Character; if not r then return end
        local root = r:FindFirstChild("HumanoidRootPart"); if not root then return end
        local cf = Camera.CFrame
        local fwd = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z)
        local rgt = Vector3.new(cf.RightVector.X, 0, cf.RightVector.Z)
        if fwd.Magnitude > 0 then fwd = fwd.Unit end
        if rgt.Magnitude > 0 then rgt = rgt.Unit end
        local up = Vector3.new(0, 1, 0); local dir = Vector3.zero
        if flyKeys[Enum.KeyCode.W] then dir += fwd end
        if flyKeys[Enum.KeyCode.S] then dir -= fwd end
        if flyKeys[Enum.KeyCode.D] then dir += rgt end
        if flyKeys[Enum.KeyCode.A] then dir -= rgt end
        if flyKeys[Enum.KeyCode.Space] then dir += up end
        if flyKeys[Enum.KeyCode.LeftShift] then dir -= up end
        if flyKeys[Enum.KeyCode.LeftControl] then dir -= up end
        flyBV.Velocity = dir.Magnitude > 0 and dir.Unit * FlySettings.Speed or Vector3.zero
        local flat = Vector3.new(dir.X, 0, dir.Z)
        flyBG.CFrame = flat.Magnitude > 0 and CFrame.lookAt(root.Position, root.Position + flat.Unit) or CFrame.lookAt(root.Position, root.Position + fwd)
    end)
end

local function disableFly()
    flyBV.Parent = nil; flyBG.Parent = nil
    for _, c in pairs(flyConns) do c:Disconnect() end
    flyConns = {}; flyKeys = {}
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    if hum then hum:ChangeState(Enum.HumanoidStateType.GettingUp) end
end

LocalPlayer.CharacterAdded:Connect(function() task.wait(0.5); if FlySettings.Enabled then enableFly() end end)

local FreeCam = { Enabled = false, Speed = 50 }
local FC = {
    Active = false, Pitch = 0, Yaw = 0, Pos = Vector3.zero, Keys = {},
    SavedSubject = nil, SavedType = nil, SavedWS = nil, SavedJP = nil,
    SavedAR = nil, SavedAnc = nil, Conns = {}
}

local function FC_Enable()
    if FC.Active then return end; FC.Active = true
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    if hum then
        pcall(function() FC.SavedWS = hum.WalkSpeed end)
        pcall(function() FC.SavedJP = hum.JumpPower end)
        pcall(function() FC.SavedAR = hum.AutoRotate end)
        pcall(function() hum.WalkSpeed = 0 end)
        pcall(function() hum.JumpPower = 0 end)
        pcall(function() hum.AutoRotate = false end)
    end
    if hrp then FC.SavedAnc = hrp.Anchored; hrp.Anchored = true end
    FC.SavedSubject = Camera.CameraSubject; FC.SavedType = Camera.CameraType
    Camera.CameraType = Enum.CameraType.Scriptable; Camera.CameraSubject = nil
    local lv = Camera.CFrame.LookVector
    FC.Pitch = math.asin(math.clamp(lv.Y, -1, 1))
    FC.Yaw = math.atan2(-lv.X, -lv.Z)
    FC.Pos = Camera.CFrame.Position
    if not IsMobile then UserInputService.MouseBehavior = Enum.MouseBehavior.LockCenter end
    FC.Conns[1] = UserInputService.InputBegan:Connect(function(i, g) if not g then FC.Keys[i.KeyCode] = true end end)
    FC.Conns[2] = UserInputService.InputEnded:Connect(function(i) FC.Keys[i.KeyCode] = false end)
    FC.Conns[3] = RunService.RenderStepped:Connect(function(dt)
        if not FC.Active then return end
        if not IsMobile then
            local d = UserInputService:GetMouseDelta()
            FC.Yaw = FC.Yaw - d.X * 0.003
            FC.Pitch = math.clamp(FC.Pitch - d.Y * 0.003, -math.rad(89), math.rad(89))
        end
        local rot = CFrame.Angles(0, FC.Yaw, 0) * CFrame.Angles(FC.Pitch, 0, 0)
        local mv = Vector3.zero
        if FC.Keys[Enum.KeyCode.W] then mv += rot.LookVector end
        if FC.Keys[Enum.KeyCode.S] then mv -= rot.LookVector end
        if FC.Keys[Enum.KeyCode.D] then mv += rot.RightVector end
        if FC.Keys[Enum.KeyCode.A] then mv -= rot.RightVector end
        if FC.Keys[Enum.KeyCode.E] then mv += Vector3.new(0, 1, 0) end
        if FC.Keys[Enum.KeyCode.Q] then mv -= Vector3.new(0, 1, 0) end
        if mv.Magnitude > 0 then FC.Pos += mv.Unit * FreeCam.Speed * dt end
        Camera.CFrame = CFrame.new(FC.Pos) * rot
        Camera.Focus = Camera.CFrame * CFrame.new(0, 0, -10)
    end)
end

local function FC_Disable()
    if not FC.Active then return end; FC.Active = false
    for _, c in pairs(FC.Conns) do c:Disconnect() end; FC.Conns = {}
    Camera.CameraType = FC.SavedType or Enum.CameraType.Custom
    Camera.CameraSubject = FC.SavedSubject
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    local hrp = char and char:FindFirstChild("HumanoidRootPart")
    if hum then
        pcall(function() hum.WalkSpeed = FC.SavedWS or 16 end)
        pcall(function() hum.JumpPower = FC.SavedJP or 50 end)
        pcall(function() hum.AutoRotate = FC.SavedAR ~= false end)
    end
    if hrp then hrp.Anchored = FC.SavedAnc or false end
    if not IsMobile then UserInputService.MouseBehavior = Enum.MouseBehavior.Default end
    FC.Keys = {}
end

local Aimbot = {
    Enabled = false, FOVRadius = 150, Smoothing = 5, VisibleCheck = false,
    Prediction = 0, HitChance = 100, TargetPart = "Head", TeamCheck = false
}
local AbFOV = Drawing.new("Circle")
AbFOV.Visible = false; AbFOV.Color = Color3.fromRGB(255, 255, 255)
AbFOV.Thickness = 1.5; AbFOV.Filled = false; AbFOV.NumSides = 64; AbFOV.Transparency = 1
local Ab_Holding = false; local AbConns = {}

local function Ab_GetTarget()
    local best, bestD = nil, Aimbot.FOVRadius
    local cen = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
    for _, pl in ipairs(Players:GetPlayers()) do
        if pl == LocalPlayer then continue end
        if Aimbot.TeamCheck and pl.Team and LocalPlayer.Team and pl.Team == LocalPlayer.Team then continue end
        local char = pl.Character; if not char then continue end
        local hum = char:FindFirstChildOfClass("Humanoid"); if not hum or hum.Health <= 0 then continue end
        local part = char:FindFirstChild(Aimbot.TargetPart) or char:FindFirstChild("Head"); if not part then continue end
        if Aimbot.VisibleCheck then
            local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Blacklist
            p.FilterDescendantsInstances = { LocalPlayer.Character or workspace }
            local res = workspace:Raycast(Camera.CFrame.Position, part.Position - Camera.CFrame.Position, p)
            if res and not res.Instance:IsDescendantOf(char) then continue end
        end
        local sp, on = Camera:WorldToViewportPoint(part.Position); if not on or sp.Z <= 0 then continue end
        local d = (Vector2.new(sp.X, sp.Y) - cen).Magnitude
        if d < bestD then bestD = d; best = part end
    end
    return best
end

local function Ab_Step()
    if not Aimbot.Enabled or not Ab_Holding then return end
    if Aimbot.HitChance < 100 and math.random(1, 100) > Aimbot.HitChance then return end
    local part = Ab_GetTarget(); if not part then return end
    local tPos = part.Position
    if Aimbot.Prediction > 0 then
        local h = part.Parent and part.Parent:FindFirstChild("HumanoidRootPart")
        if h then tPos += h.AssemblyLinearVelocity * Aimbot.Prediction end
    end
    local sp, on = Camera:WorldToViewportPoint(tPos); if not on or sp.Z <= 0 then return end
    local dx = sp.X - Camera.ViewportSize.X / 2; local dy = sp.Y - Camera.ViewportSize.Y / 2
    local sm = math.max(1, Aimbot.Smoothing)
    if math.abs(dx) > 0.1 or math.abs(dy) > 0.1 then mousemoverel(dx / sm, dy / sm) end
end

local function Ab_Start()
    if AbConns[1] then return end; Ab_Holding = false; AbFOV.Visible = true
    AbConns[1] = RunService.RenderStepped:Connect(function()
        AbFOV.Position = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
        AbFOV.Radius = Aimbot.FOVRadius
    end)
    AbConns[2] = UserInputService.InputBegan:Connect(function(i, g)
        if not g and i.UserInputType == Enum.UserInputType.MouseButton2 then Ab_Holding = true end
    end)
    AbConns[3] = UserInputService.InputEnded:Connect(function(i)
        if i.UserInputType == Enum.UserInputType.MouseButton2 then Ab_Holding = false end
    end)
    AbConns[4] = RunService.RenderStepped:Connect(Ab_Step)
end

local function Ab_Stop()
    Ab_Holding = false; AbFOV.Visible = false
    for _, c in pairs(AbConns) do c:Disconnect() end; AbConns = {}
end

local SA = { enabled = false, FOVRadius = 70, visibleCheck = false }
local SA_Conns = {}
local SA_FOV = Drawing.new("Circle")
SA_FOV.Visible = false; SA_FOV.Color = Color3.fromRGB(255, 255, 255)
SA_FOV.Thickness = 1.5; SA_FOV.Filled = false; SA_FOV.NumSides = 64

local function SA_getNearestHead()
    local best, bestDist = nil, SA.FOVRadius
    local center = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
    for _, pl in ipairs(Players:GetPlayers()) do
        if pl == LocalPlayer then continue end
        local char = pl.Character; if not char then continue end
        local hum = char:FindFirstChildOfClass("Humanoid"); if not hum or hum.Health <= 0 then continue end
        local head = char:FindFirstChild("Head"); if not head then continue end
        local sp, on = Camera:WorldToViewportPoint(head.Position)
        if not on or sp.Z <= 0 then continue end
        local dist = (Vector2.new(sp.X, sp.Y) - center).Magnitude
        if dist < bestDist then bestDist = dist; best = head end
    end
    return best
end

local function SA_start()
    SA_FOV.Visible = true
    SA_Conns[1] = RunService.RenderStepped:Connect(function()
        SA_FOV.Position = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
        SA_FOV.Radius = SA.FOVRadius
    end)
    SA_Conns[2] = UserInputService.InputBegan:Connect(function(i, g)
        if g then return end
        if i.UserInputType == Enum.UserInputType.MouseButton1 or i.KeyCode == Enum.KeyCode.ButtonR2 then
            local targetHead = SA_getNearestHead()
            if targetHead then
                Camera.CFrame = CFrame.new(Camera.CFrame.Position, targetHead.Position)
                pcall(function() ReplicatedStorage.Remotes.Attack:FireServer(targetHead) end)
            end
        end
    end)
end

local function SA_stop()
    SA_FOV.Visible = false
    for _, c in pairs(SA_Conns) do c:Disconnect() end; SA_Conns = {}
end

local AntiHit = { Enabled = false, Blocked = {} }
local ANTI_HIT_ITEMS = { ["Riot Shield"] = { "Riot Shield", "RiotShield", "Shield" } }

local function AH_getRawVMNames(player)
    local vm = workspace:FindFirstChild("ViewModels"); if not vm then return {} end
    local results = {}; local prefixes = { player.Name .. " - ", player.DisplayName .. " - " }
    for _, child in ipairs(vm:GetChildren()) do
        local n = child.Name
        for _, pf in ipairs(prefixes) do
            if #n >= #pf and n:sub(1, #pf) == pf then results[n] = true; break end
        end
    end
    return results
end

local function AH_playerIsProtected(player)
    if not AntiHit.Enabled then return false end
    if not next(AntiHit.Blocked) then return false end
    local rawNames = AH_getRawVMNames(player)
    for friendlyName in pairs(AntiHit.Blocked) do
        local keywords = ANTI_HIT_ITEMS[friendlyName]
        if keywords then
            for rawName in pairs(rawNames) do
                local lowerRaw = rawName:lower()
                for _, kw in ipairs(keywords) do
                    if lowerRaw:find(kw:lower(), 1, true) then return true end
                end
            end
        end
    end
    return false
end

local AS = {
    enabled = false, TargetParts = { "Head" }, fireRate = 0.08,
    maxDist = 1000, lastFire = 0, threshold = 40, thread = nil
}
local AS_vp = RaycastParams.new()
AS_vp.FilterType = Enum.RaycastFilterType.Blacklist
AS_vp.IgnoreWater = true

local function AS_visible(part, char)
    local lc = LocalPlayer.Character
    AS_vp.FilterDescendantsInstances = lc and { lc } or {}
    local res = workspace:Raycast(Camera.CFrame.Position, part.Position - Camera.CFrame.Position, AS_vp)
    if not res then return false end
    return res.Instance and res.Instance:IsDescendantOf(char)
end

local function AS_findTarget()
    local best, bd = nil, AS.threshold
    local sc = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
    local lc = LocalPlayer.Character
    local lhrp = lc and lc:FindFirstChild("HumanoidRootPart")
    for _, pl in ipairs(Players:GetPlayers()) do
        if pl == LocalPlayer then continue end
        local char = pl.Character; if not char then continue end
        local hum = char:FindFirstChildOfClass("Humanoid"); if not hum or hum.Health <= 0 then continue end
        if AH_playerIsProtected(pl) then continue end
        local tp = nil
        for _, pn in ipairs(AS.TargetParts) do local p = char:FindFirstChild(pn); if p then tp = p; break end end
        if not tp then continue end
        local sp, on = Camera:WorldToViewportPoint(tp.Position); if not on or sp.Z <= 0 then continue end
        if not AS_visible(tp, char) then continue end
        if lhrp then
            local h = char:FindFirstChild("HumanoidRootPart")
            if h and (h.Position - lhrp.Position).Magnitude > AS.maxDist then continue end
        end
        local d = (Vector2.new(sp.X, sp.Y) - sc).Magnitude
        if d < bd then bd = d; best = pl end
    end
    return best
end

local function AS_start()
    AS.lastFire = 0
    AS.thread = task.spawn(function()
        while AS.enabled do
            local now = tick()
            if now - AS.lastFire >= AS.fireRate then
                if AS_findTarget() then
                    AS.lastFire = now; mouse1click(); task.wait(AS.fireRate)
                else task.wait(0.05) end
            else task.wait(AS.fireRate - (now - AS.lastFire)) end
        end
    end)
end

local function AS_stop()
    AS.enabled = false
    if AS.thread then task.cancel(AS.thread); AS.thread = nil end
end

local AG = { Enabled = false, BlockedSet = {} }
local AG_Conns = {}
local PGui = LocalPlayer:WaitForChild("PlayerGui")

local GADGET_MAP = {
    ["Smoke Grenade"] = { workspace = { "Smoke Grenade" } },
    ["Flashbang"] = { workspace = { "Throwable - Flashbang" }, gui = { "Flashbang", "FlashbangEffect", "FlashEffect", "Flash", "ScreenFlash", "FlashGui" } },
    ["Molotov"] = { workspace = { "MolotovAnchor", "MolotovFire", "MolotovDamage", "Molotov" } },
}
local LIGHTING_FX = { "ColorCorrectionEffect", "BlurEffect", "BloomEffect" }

local function tryDel(i) if i and i.Parent then pcall(function() i:Destroy() end) end end
local function shouldBlock(inst)
    for gadgetName in pairs(AG.BlockedSet) do
        local map = GADGET_MAP[gadgetName]; if map then
            if map.workspace then for _, n in ipairs(map.workspace) do if inst.Name == n then return true end end end
            if map.gui then for _, n in ipairs(map.gui) do if inst.Name == n then return true end end end
        end
    end
    return false
end
local function isLightingFX(inst)
    if not next(AG.BlockedSet) then return false end
    for _, cls in ipairs(LIGHTING_FX) do
        if inst:IsA(cls) and (inst.Parent == Lighting or inst.Parent == Camera) then return true end
    end
    return false
end
local function chkAny(inst)
    if not inst or not inst.Parent then return end
    if shouldBlock(inst) or isLightingFX(inst) then tryDel(inst) end
end
local function AG_start()
    for _, d in ipairs(workspace:GetDescendants()) do chkAny(d) end
    for _, d in ipairs(PGui:GetDescendants()) do chkAny(d) end
    for _, d in ipairs(Lighting:GetDescendants()) do chkAny(d) end
    AG_Conns[1] = workspace.DescendantAdded:Connect(function(i) if AG.Enabled then task.defer(function() chkAny(i) end) end end)
    AG_Conns[2] = PGui.DescendantAdded:Connect(function(i) if AG.Enabled then task.defer(function() chkAny(i) end) end end)
    AG_Conns[3] = Lighting.DescendantAdded:Connect(function(i) if AG.Enabled then task.defer(function() chkAny(i) end) end end)
end
local function AG_stop() for _, c in pairs(AG_Conns) do c:Disconnect() end; AG_Conns = {} end

local TrapESP = { SubspaceTripmine = false, Color = Color3.fromRGB(170, 0, 255) }
local tripObjs = {}; local tripConns = {}

local function addTripmine(inst)
    for _, o in ipairs(tripObjs) do if o.inst == inst then return end end
    local hl = Instance.new("SelectionBox")
    hl.Color3 = TrapESP.Color; hl.LineThickness = 0.05
    hl.SurfaceTransparency = 0.5; hl.SurfaceColor3 = TrapESP.Color
    hl.Adornee = inst; hl.Parent = workspace
    local bb = Instance.new("BillboardGui")
    bb.Name = "TripESP"; bb.AlwaysOnTop = true
    bb.Size = UDim2.new(0, 140, 0, 26); bb.StudsOffset = Vector3.new(0, 3, 0)
    bb.Adornee = inst; bb.Parent = workspace
    local lbl = Instance.new("TextLabel")
    lbl.Size = UDim2.new(1, 0, 1, 0); lbl.BackgroundTransparency = 1
    lbl.TextStrokeTransparency = 0; lbl.TextStrokeColor3 = Color3.new(0, 0, 0)
    lbl.TextColor3 = TrapESP.Color; lbl.Font = Enum.Font.GothamBold
    lbl.TextScaled = true; lbl.Text = "⚡ Subspace Tripmine"; lbl.Parent = bb
    table.insert(tripObjs, { inst = inst, hl = hl, bb = bb, lbl = lbl })
end

local function cleanTrip()
    local i = 1
    while i <= #tripObjs do
        local o = tripObjs[i]
        if not o.inst or not o.inst.Parent then
            pcall(function() o.hl:Destroy() end)
            pcall(function() o.bb:Destroy() end)
            table.remove(tripObjs, i)
        else
            o.hl.Color3 = TrapESP.Color; o.hl.SurfaceColor3 = TrapESP.Color
            o.lbl.TextColor3 = TrapESP.Color; i += 1
        end
    end
end

local function clearTrip()
    for _, o in ipairs(tripObjs) do
        pcall(function() o.hl:Destroy() end)
        pcall(function() o.bb:Destroy() end)
    end
    tripObjs = {}
end

local function startTrip()
    for _, d in ipairs(workspace:GetDescendants()) do
        if d.Name == "SubspaceTripmineHitbox" then addTripmine(d) end
    end
    tripConns[1] = workspace.DescendantAdded:Connect(function(i)
        if TrapESP.SubspaceTripmine and i.Name == "SubspaceTripmineHitbox" then
            task.defer(function() addTripmine(i) end)
        end
    end)
    tripConns[2] = RunService.Heartbeat:Connect(cleanTrip)
end

local function stopTrip()
    for _, c in pairs(tripConns) do c:Disconnect() end
    tripConns = {}; clearTrip()
end


local HotbarESP = {
    Enabled = false,
    ActiveColor = Color3.fromRGB(255, 255, 255),
    InactiveColor = Color3.fromRGB(130, 130, 130),
    ActiveStroke = Color3.fromRGB(70, 140, 255),
    MaxDistance = 100
}
local hbCache = {}; local hbState = {}; local hbConns = {}
local SLOT_MAX = 4; local SW, SH, SP_GAP = 80, 30, 4
local TW = SLOT_MAX * (SW + SP_GAP) - SP_GAP

local function getPlayerPrefixes(player)
    return { player.Name .. " - ", player.DisplayName .. " - " }
end

local function nameMatchesPlayer(name, prefixes)
    for _, pf in ipairs(prefixes) do
        if #name >= #pf and name:sub(1, #pf) == pf then return true end
    end
    return false
end

local function getRawVMNames(player)
    local vm = workspace:FindFirstChild("ViewModels"); if not vm then return {} end
    local results = {}
    local prefixes = getPlayerPrefixes(player)
    for _, child in ipairs(vm:GetChildren()) do
        if nameMatchesPlayer(child.Name, prefixes) then
            results[child.Name] = true
        end
    end
    return results
end

local function extractGunName(raw)
    local last = nil; local s2 = 1
    while true do
        local s, e = raw:find(" %- ", s2); if not s then break end
        last = e + 1; s2 = s + 1
    end
    if last then local name = raw:sub(last):match("^%s*(.-)%s*$"); if name and #name > 0 then return name end end
    return raw
end

local function buildSlotFrame(parent, idx)
    local sf = Instance.new("Frame"); sf.Name = "Slot" .. idx
    sf.Size = UDim2.new(0, SW, 0, SH); sf.Position = UDim2.new(0, (idx - 1) * (SW + SP_GAP), 0, 2)
    sf.BackgroundColor3 = Color3.fromRGB(10, 10, 10); sf.BackgroundTransparency = 0.25
    sf.BorderSizePixel = 0; sf.Parent = parent
    Instance.new("UICorner", sf).CornerRadius = UDim.new(0, 6)
    local stroke = Instance.new("UIStroke", sf); stroke.Color = Color3.fromRGB(55, 55, 55)
    stroke.Thickness = 1; stroke.Transparency = 0.3
    local numLbl = Instance.new("TextLabel", sf)
    numLbl.Size = UDim2.new(0, 12, 0, 12); numLbl.Position = UDim2.new(0, 3, 0, 2)
    numLbl.BackgroundTransparency = 1; numLbl.Text = tostring(idx)
    numLbl.TextColor3 = Color3.fromRGB(90, 90, 90); numLbl.Font = Enum.Font.GothamBold
    numLbl.TextSize = 9; numLbl.TextXAlignment = Enum.TextXAlignment.Left
    numLbl.TextYAlignment = Enum.TextYAlignment.Top
    local gunLbl = Instance.new("TextLabel", sf); gunLbl.Name = "GunLbl"
    gunLbl.Size = UDim2.new(1, -6, 1, 0); gunLbl.Position = UDim2.new(0, 3, 0, 0)
    gunLbl.BackgroundTransparency = 1; gunLbl.Text = ""
    gunLbl.TextColor3 = Color3.fromRGB(200, 200, 200); gunLbl.Font = Enum.Font.GothamBold
    gunLbl.TextSize = 11; gunLbl.TextTruncate = Enum.TextTruncate.AtEnd
    gunLbl.TextXAlignment = Enum.TextXAlignment.Center
    gunLbl.TextYAlignment = Enum.TextYAlignment.Center
    return { frame = sf, lbl = gunLbl, stroke = stroke }
end

local function createHBBillboard(player)
    local char = player.Character
    local head = char and char:FindFirstChild("Head"); if not head then return end
    if hbCache[player] then pcall(function() hbCache[player].gui:Destroy() end); hbCache[player] = nil end
    local bb = Instance.new("BillboardGui")
    bb.Name = "HotbarESP_" .. player.Name; bb.AlwaysOnTop = true
    bb.Size = UDim2.new(0, TW, 0, SH + 6); bb.StudsOffset = Vector3.new(0, 3.5, 0)
    bb.Adornee = head; bb.ResetOnSpawn = false; bb.ClipsDescendants = false; bb.Parent = workspace
    local bg = Instance.new("Frame", bb); bg.Size = UDim2.new(1, 0, 1, 0)
    bg.BackgroundTransparency = 1; bg.BorderSizePixel = 0
    local slots = {}; for i = 1, SLOT_MAX do slots[i] = buildSlotFrame(bg, i) end
    hbCache[player] = { gui = bb, slots = slots }
    
    hbState[player] = { slotMap = {}, slotCount = 0, activeRaw = nil }
end

local function removeHB(player)
    if hbCache[player] then pcall(function() hbCache[player].gui:Destroy() end); hbCache[player] = nil end
    hbState[player] = nil
end

local function updateHB(player)
    local data = hbCache[player]; if not data then return end
    local char = player.Character
    local head = char and char:FindFirstChild("Head")
    if not char or not head then data.gui.Enabled = false; return end
    local lc = LocalPlayer.Character
    local lhrp = lc and lc:FindFirstChild("HumanoidRootPart")
    local phrp = char:FindFirstChild("HumanoidRootPart")
    if HotbarESP.MaxDistance > 0 and lhrp and phrp then
        if (phrp.Position - lhrp.Position).Magnitude > HotbarESP.MaxDistance then
            data.gui.Enabled = false; return
        end
    end
    local _, onScreen = Camera:WorldToViewportPoint(head.Position)
    if not onScreen then data.gui.Enabled = false; return end
    data.gui.Enabled = true; data.gui.Adornee = head

    local state = hbState[player]
    if not state then
        hbState[player] = { slotMap = {}, slotCount = 0, activeRaw = nil }
        state = hbState[player]
    end

    
    local currentRaw = getRawVMNames(player)




    for rawName in pairs(currentRaw) do
        if not state.slotMap[rawName] then
            if state.slotCount < SLOT_MAX then
                state.slotCount = state.slotCount + 1
                state.slotMap[rawName] = state.slotCount
            else
                
                local reuseSlot = nil
                local reuseKey = nil
                for existingRaw, slotIdx in pairs(state.slotMap) do
                    if not currentRaw[existingRaw] then
                        reuseSlot = slotIdx; reuseKey = existingRaw; break
                    end
                end
                if reuseSlot then
                    state.slotMap[reuseKey] = nil
                    state.slotMap[rawName] = reuseSlot
                end
            end
        end
    end

    
    local slotToRaw = {}
    for rawName, slotIdx in pairs(state.slotMap) do
        if currentRaw[rawName] then
            slotToRaw[slotIdx] = rawName
        end
    end

    local activeRaw = state.activeRaw
    
    if activeRaw and not currentRaw[activeRaw] then
        activeRaw = nil; state.activeRaw = nil
    end
    
    if not activeRaw then
        for i = 1, SLOT_MAX do
            if slotToRaw[i] then activeRaw = slotToRaw[i]; state.activeRaw = activeRaw; break end
        end
    end

    
    for i = 1, SLOT_MAX do
        local sf = data.slots[i]
        local raw = slotToRaw[i]
        if raw then
            local display = extractGunName(raw)
            local isActive = (raw == activeRaw)
            if isActive then
                sf.frame.BackgroundColor3 = Color3.fromRGB(12, 30, 60)
                sf.frame.BackgroundTransparency = 0.05
                sf.stroke.Color = HotbarESP.ActiveStroke
                sf.stroke.Transparency = 0; sf.stroke.Thickness = 1.8
                sf.lbl.Text = display; sf.lbl.TextColor3 = HotbarESP.ActiveColor
                sf.lbl.Font = Enum.Font.GothamBold
            else
                sf.frame.BackgroundColor3 = Color3.fromRGB(14, 14, 14)
                sf.frame.BackgroundTransparency = 0.3
                sf.stroke.Color = Color3.fromRGB(45, 45, 45)
                sf.stroke.Transparency = 0.5; sf.stroke.Thickness = 1
                sf.lbl.Text = display; sf.lbl.TextColor3 = HotbarESP.InactiveColor
                sf.lbl.Font = Enum.Font.Gotham
            end
        else
            sf.frame.BackgroundColor3 = Color3.fromRGB(8, 8, 8)
            sf.frame.BackgroundTransparency = 0.5
            sf.stroke.Color = Color3.fromRGB(28, 28, 28)
            sf.stroke.Transparency = 0.7; sf.stroke.Thickness = 1
            sf.lbl.Text = ""
        end
    end
end

local function refreshHBColors()
    for player, data in pairs(hbCache) do
        local state = hbState[player]; if not state or not data.slots then continue end
        local currentRaw = getRawVMNames(player)
        local slotToRaw = {}
        for rawName, slotIdx in pairs(state.slotMap) do
            if currentRaw[rawName] then slotToRaw[slotIdx] = rawName end
        end
        for i = 1, SLOT_MAX do
            local sf = data.slots[i]; local raw = slotToRaw[i]
            if raw and sf then
                if raw == state.activeRaw then
                    sf.lbl.TextColor3 = HotbarESP.ActiveColor
                    sf.stroke.Color = HotbarESP.ActiveStroke
                else
                    sf.lbl.TextColor3 = HotbarESP.InactiveColor
                end
            end
        end
    end
end

local vmWatchConns = {}
local function watchVM(player)
    if vmWatchConns[player] then vmWatchConns[player]:Disconnect(); vmWatchConns[player] = nil end
    local vm = workspace:FindFirstChild("ViewModels"); if not vm then return end
    local prefixes = getPlayerPrefixes(player)
    vmWatchConns[player] = vm.ChildAdded:Connect(function(child)
        if not HotbarESP.Enabled then return end
        if not nameMatchesPlayer(child.Name, prefixes) then return end
        local state = hbState[player]
        if not state then return end
        local rawName = child.Name
        
        state.activeRaw = rawName
        
        if not state.slotMap[rawName] then
            if state.slotCount < SLOT_MAX then
                state.slotCount = state.slotCount + 1
                state.slotMap[rawName] = state.slotCount
            else
                
                local currentRaw = getRawVMNames(player)
                local reuseSlot = nil; local reuseKey = nil
                for existingRaw, slotIdx in pairs(state.slotMap) do
                    if not currentRaw[existingRaw] then
                        reuseSlot = slotIdx; reuseKey = existingRaw; break
                    end
                end
                if reuseSlot then
                    state.slotMap[reuseKey] = nil
                    state.slotMap[rawName] = reuseSlot
                end
            end
        end
    end)
end

local function setupHBPlayer(player)
    if player == LocalPlayer then return end
    createHBBillboard(player); watchVM(player)
    player.CharacterAdded:Connect(function()
        task.wait(0.8)
        if HotbarESP.Enabled then createHBBillboard(player); watchVM(player) end
    end)
end

local function startHB()
    for _, pl in ipairs(Players:GetPlayers()) do if pl ~= LocalPlayer then setupHBPlayer(pl) end end
    hbConns[1] = Players.PlayerAdded:Connect(function(pl)
        task.wait(1); if HotbarESP.Enabled then setupHBPlayer(pl) end
    end)
    local lastT = 0
    hbConns[2] = RunService.RenderStepped:Connect(function()
        if not HotbarESP.Enabled then return end
        local now = tick(); if now - lastT < 0.08 then return end; lastT = now
        for pl in pairs(hbCache) do
            if not pl or not pl.Parent then
                removeHB(pl)
                if vmWatchConns[pl] then vmWatchConns[pl]:Disconnect(); vmWatchConns[pl] = nil end
            else updateHB(pl) end
        end
    end)
end

local function stopHB()
    for _, c in pairs(hbConns) do c:Disconnect() end; hbConns = {}
    for pl in pairs(vmWatchConns) do vmWatchConns[pl]:Disconnect() end; vmWatchConns = {}
    for pl in pairs(hbCache) do removeHB(pl) end; hbCache = {}; hbState = {}
end

local ESPS = {
    Enabled = false, Box = false, Skeleton = false, HealthBar = false,
    Distance = false, SnapLines = false, Names = false,
    BoxColor = Color3.fromRGB(255, 50, 50),
    SkeletonColor = Color3.fromRGB(255, 255, 255),
    HealthHigh = Color3.fromRGB(0, 255, 100),
    HealthLow = Color3.fromRGB(255, 50, 50),
    DistColor = Color3.fromRGB(255, 255, 100),
    SnapColor = Color3.fromRGB(255, 50, 50),
    NameColor = Color3.fromRGB(255, 255, 255),
    MaxDist = IsMobile and 400 or 1000, MinDist = 0,
    TeamCheck = false, SnapOrigin = "Bottom",
}
local ESPCache = {}; local ESP_IVL = 1 / 20; local ESP_last = 0

local BT = { Enabled = false, Color = Color3.fromRGB(255, 60, 60), FadeTime = 0.3, Thickness = 0.05, Style = "Straight" }
local BT_conn = nil

local function BT_makePart(col, thick)
    local p = Instance.new("Part"); p.Name = "BT_Line"; p.Anchored = true
    p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
    p.Material = Enum.Material.Neon; p.Color = col; p.Transparency = 0
    p.Size = Vector3.new(thick, thick, 0.01)
    return p
end

local function BT_fadeAndDestroy(parts, fadeTime)
    local steps = 15; local stepWait = fadeTime / steps
    for i = 1, steps do
        task.wait(stepWait)
        for _, p in ipairs(parts) do if p.Parent then p.Transparency = i / steps end end
    end
    for _, p in ipairs(parts) do if p.Parent then p:Destroy() end end
end

local function BT_rainbow(t) return Color3.fromHSV((t % 1), 1, 1) end

local function BT_spawnStraight(origin, hitPos, col, thick, fadeTime)
    local dist = (origin - hitPos).Magnitude; if dist < 0.5 then return end
    local p = BT_makePart(col, thick)
    p.Size = Vector3.new(thick, thick, dist)
    p.CFrame = CFrame.new(origin, hitPos) * CFrame.new(0, 0, -dist / 2)
    p.Parent = workspace
    task.spawn(BT_fadeAndDestroy, { p }, fadeTime)
end

local function BT_spawnZigzag(origin, hitPos, col, thick, fadeTime)
    local segs = 8; local parts = {}
    local dir = (hitPos - origin); local len = dir.Magnitude; if len < 0.5 then return end
    local step = len / segs; local unitDir = dir.Unit
    local perp = Vector3.new(-unitDir.Z, 0, unitDir.X)
    if perp.Magnitude < 0.01 then perp = Vector3.new(0, 1, 0) end; perp = perp.Unit
    local amplitude = math.clamp(len * 0.06, 0.3, 2.5); local prev = origin
    for i = 1, segs do
        local mid = origin + unitDir * (step * i)
        local offset = (i % 2 == 0) and amplitude or -amplitude
        if i == segs then offset = 0 end
        local next = mid + perp * offset
        local segDist = (next - prev).Magnitude
        if segDist > 0.01 then
            local p = BT_makePart(col, thick * 0.8)
            p.Size = Vector3.new(thick * 0.8, thick * 0.8, segDist)
            p.CFrame = CFrame.new(prev, next) * CFrame.new(0, 0, -segDist / 2)
            p.Parent = workspace; table.insert(parts, p)
        end
        prev = next
    end
    task.spawn(BT_fadeAndDestroy, parts, fadeTime)
end

local function BT_spawnLightning(origin, hitPos, col, thick, fadeTime)
    local segs = 12; local parts = {}
    local dir = (hitPos - origin); local len = dir.Magnitude; if len < 0.5 then return end
    local unitDir = dir.Unit; local amplitude = math.clamp(len * 0.08, 0.5, 3.5)
    local points = { origin }
    for i = 1, segs - 1 do
        local base = origin + unitDir * (len * (i / segs))
        local rx = (math.random() - 0.5) * 2 * amplitude
        local ry = (math.random() - 0.5) * 2 * amplitude
        local perp1 = Vector3.new(-unitDir.Z, 0, unitDir.X)
        if perp1.Magnitude < 0.01 then perp1 = Vector3.new(1, 0, 0) end; perp1 = perp1.Unit
        local perp2 = unitDir:Cross(perp1).Unit
        table.insert(points, base + perp1 * rx + perp2 * ry)
    end
    table.insert(points, hitPos)
    for i = 1, #points - 1 do
        local a, b = points[i], points[i + 1]; local segDist = (b - a).Magnitude
        if segDist > 0.01 then
            local p = BT_makePart(col, thick * 0.7)
            p.Size = Vector3.new(thick * 0.7, thick * 0.7, segDist)
            p.CFrame = CFrame.new(a, b) * CFrame.new(0, 0, -segDist / 2)
            p.Parent = workspace; table.insert(parts, p)
        end
    end
    task.spawn(BT_fadeAndDestroy, parts, fadeTime)
end

local function BT_spawnRainbow(origin, hitPos, thick, fadeTime)
    local segs = 16; local parts = {}
    local dir = (hitPos - origin); local len = dir.Magnitude; if len < 0.5 then return end
    local unitDir = dir.Unit; local segLen = len / segs; local t0 = tick() % 1
    for i = 0, segs - 1 do
        local a = origin + unitDir * (segLen * i)
        local b = origin + unitDir * (segLen * (i + 1))
        local segDist = (b - a).Magnitude
        if segDist > 0.01 then
            local col = BT_rainbow(t0 + i / segs)
            local p = BT_makePart(col, thick)
            p.Size = Vector3.new(thick, thick, segDist)
            p.CFrame = CFrame.new(a, b) * CFrame.new(0, 0, -segDist / 2)
            p.Parent = workspace; table.insert(parts, p)
        end
    end
    task.spawn(BT_fadeAndDestroy, parts, fadeTime)
end

local function BT_drawTracer(tracerFolder)
    task.defer(function()
        if not tracerFolder or not tracerFolder.Parent then return end
        local a0, a1; local deadline = tick() + 0.1
        repeat
            a0 = tracerFolder:FindFirstChild("Attachment0")
            a1 = tracerFolder:FindFirstChild("Attachment1")
            if not (a0 and a1) then task.wait() end
        until (a0 and a1) or tick() > deadline
        if not (a0 and a1) then return end
        local origin = a0.WorldPosition; local hitPos = a1.WorldPosition
        local style = BT.Style; local col = BT.Color; local thick = BT.Thickness; local fade = BT.FadeTime
        if style == "Straight" then BT_spawnStraight(origin, hitPos, col, thick, fade)
        elseif style == "Zigzag" then BT_spawnZigzag(origin, hitPos, col, thick, fade)
        elseif style == "Lightning" then BT_spawnLightning(origin, hitPos, col, thick, fade)
        elseif style == "Rainbow" then BT_spawnRainbow(origin, hitPos, thick, fade) end
    end)
end

local function BT_start()
    if BT_conn then return end
    BT_conn = workspace.DescendantAdded:Connect(function(inst)
        if not BT.Enabled then return end
        if inst.Name == "TracerEffect" then BT_drawTracer(inst) end
    end)
end

local function BT_stop()
    if BT_conn then BT_conn:Disconnect(); BT_conn = nil end
    for _, v in ipairs(workspace:GetDescendants()) do
        if v.Name == "BT_Line" then v:Destroy() end
    end
end

local function lerpC(a, b, t)
    return Color3.new(a.R + (b.R - a.R) * t, a.G + (b.G - a.G) * t, a.B + (b.B - a.B) * t)
end
local function toSc(pos)
    local s, on = Camera:WorldToViewportPoint(pos)
    return Vector2.new(s.X, s.Y), on, s.Z
end

local function charBounds(char)
    local hrp = char:FindFirstChild("HumanoidRootPart")
    local head = char:FindFirstChild("Head"); if not hrp then return nil end
    local headPos = head and head.Position or (hrp.Position + Vector3.new(0, 2.5, 0))
    local feetPos = hrp.Position - Vector3.new(0, 3, 0)
    local topWorld = headPos + Vector3.new(0, 0.5, 0); local botWorld = feetPos
    local offsets = { Vector3.new(-1.2, 0, 0), Vector3.new(1.2, 0, 0), Vector3.new(0, 0, -0.6), Vector3.new(0, 0, 0.6) }
    local allPoints = {}
    for _, off in ipairs(offsets) do
        table.insert(allPoints, topWorld + off); table.insert(allPoints, botWorld + off)
    end
    table.insert(allPoints, topWorld); table.insert(allPoints, botWorld)
    local mnX, mnY, mxX, mxY = math.huge, math.huge, -math.huge, -math.huge; local any = false
    for _, pt in ipairs(allPoints) do
        local sv = Camera:WorldToViewportPoint(pt)
        local sx, sy, sz = sv.X, sv.Y, sv.Z
        if sz > 0 then
            any = true
            if sx < mnX then mnX = sx end; if sy < mnY then mnY = sy end
            if sx > mxX then mxX = sx end; if sy > mxY then mxY = sy end
        end
    end
    if not any then return nil end
    local w = mxX - mnX; local h = mxY - mnY
    if w < 6 then local cx = (mnX + mxX) / 2; mnX = cx - 3; mxX = cx + 3 end
    if h < 12 then local cy = (mnY + mxY) / 2; mnY = cy - 6; mxY = cy + 6 end
    return mnX, mnY, mxX, mxY
end

local function newLine(col, th)
    local d = Drawing.new("Line"); d.Thickness = th or 1.5
    d.Color = col or Color3.fromRGB(255, 255, 255); d.Transparency = 1
    d.Visible = false; d.From = Vector2.new(0, 0); d.To = Vector2.new(0, 0)
    return d
end
local function newTxt(sz, col)
    local d = Drawing.new("Text"); d.Size = sz or 13; d.Font = Drawing.Fonts.UI
    d.Color = col or Color3.fromRGB(255, 255, 255); d.Outline = true
    d.OutlineColor = Color3.fromRGB(0, 0, 0); d.Center = true
    d.Visible = false; d.Text = ""; d.Position = Vector2.new(0, 0)
    return d
end
local function hideLines(t) for i = 1, #t do t[i].Visible = false end end

local BONES = {
    { "Head", "UpperTorso" }, { "UpperTorso", "LowerTorso" },
    { "UpperTorso", "RightUpperArm" }, { "RightUpperArm", "RightHand" },
    { "UpperTorso", "LeftUpperArm" }, { "LeftUpperArm", "LeftHand" },
    { "LowerTorso", "RightUpperLeg" }, { "RightUpperLeg", "RightFoot" },
    { "LowerTorso", "LeftUpperLeg" }, { "LeftUpperLeg", "LeftFoot" }
}

local function createESP(pl)
    if pl == LocalPlayer or ESPCache[pl] then return end
    local o = {}; o.BS, o.BF = {}, {}
    for i = 1, 4 do o.BS[i] = newLine(Color3.new(0, 0, 0), 3); o.BF[i] = newLine(ESPS.BoxColor, 1.5) end
    o.SS, o.SK = {}, {}
    for i = 1, #BONES do o.SS[i] = newLine(Color3.new(0, 0, 0), 3); o.SK[i] = newLine(ESPS.SkeletonColor, 1.5) end
    o.HBO = newLine(Color3.new(0, 0, 0), 3); o.HBG = newLine(Color3.fromRGB(40, 40, 40), 2)
    o.HB = newLine(ESPS.HealthHigh, 2); o.HT = newTxt(10, Color3.fromRGB(255, 255, 255))
    o.NL = newTxt(13, ESPS.NameColor); o.DL = newTxt(11, ESPS.DistColor)
    o.SLO = newLine(Color3.new(0, 0, 0), 2.5); o.SL = newLine(ESPS.SnapColor, 1.2)
    ESPCache[pl] = o
end

local function removeESP(pl)
    local o = ESPCache[pl]; if not o then return end
    for _, l in ipairs(o.BS) do l:Remove() end
    for _, l in ipairs(o.BF) do l:Remove() end
    for i = 1, #o.SK do o.SS[i]:Remove(); o.SK[i]:Remove() end
    o.HBO:Remove(); o.HBG:Remove(); o.HB:Remove(); o.HT:Remove()
    o.NL:Remove(); o.DL:Remove(); o.SLO:Remove(); o.SL:Remove()
    ESPCache[pl] = nil
end

local function hideESP(o)
    hideLines(o.BS); hideLines(o.BF)
    for i = 1, #o.SK do o.SS[i].Visible = false; o.SK[i].Visible = false end
    o.HBO.Visible = false; o.HBG.Visible = false; o.HB.Visible = false; o.HT.Visible = false
    o.NL.Visible = false; o.DL.Visible = false; o.SLO.Visible = false; o.SL.Visible = false
end

local function drawBox(o, x0, y0, x1, y1)
    local c = ESPS.BoxColor; local blk = Color3.new(0, 0, 0)
    local s0, s1, s2, s3 = x0 - 1, y0 - 1, x1 + 1, y1 + 1
    o.BS[1].Color = blk; o.BS[1].From = Vector2.new(s0, s1); o.BS[1].To = Vector2.new(s2, s1); o.BS[1].Visible = true
    o.BS[2].Color = blk; o.BS[2].From = Vector2.new(s2, s1); o.BS[2].To = Vector2.new(s2, s3); o.BS[2].Visible = true
    o.BS[3].Color = blk; o.BS[3].From = Vector2.new(s2, s3); o.BS[3].To = Vector2.new(s0, s3); o.BS[3].Visible = true
    o.BS[4].Color = blk; o.BS[4].From = Vector2.new(s0, s3); o.BS[4].To = Vector2.new(s0, s1); o.BS[4].Visible = true
    o.BF[1].Color = c; o.BF[1].From = Vector2.new(x0, y0); o.BF[1].To = Vector2.new(x1, y0); o.BF[1].Visible = true
    o.BF[2].Color = c; o.BF[2].From = Vector2.new(x1, y0); o.BF[2].To = Vector2.new(x1, y1); o.BF[2].Visible = true
    o.BF[3].Color = c; o.BF[3].From = Vector2.new(x1, y1); o.BF[3].To = Vector2.new(x0, y1); o.BF[3].Visible = true
    o.BF[4].Color = c; o.BF[4].From = Vector2.new(x0, y1); o.BF[4].To = Vector2.new(x0, y0); o.BF[4].Visible = true
end

local function drawSkel(o, char)
    for i, bone in ipairs(BONES) do
        local pA = char:FindFirstChild(bone[1]); local pB = char:FindFirstChild(bone[2])
        if pA and pB then
            local sA, onA, dA = toSc(pA.Position); local sB, onB, dB = toSc(pB.Position)
            local vis = (onA or onB) and dA > 0 and dB > 0
            o.SS[i].From = sA; o.SS[i].To = sB; o.SS[i].Visible = vis
            o.SK[i].Color = ESPS.SkeletonColor; o.SK[i].From = sA; o.SK[i].To = sB; o.SK[i].Visible = vis
        else o.SS[i].Visible = false; o.SK[i].Visible = false end
    end
end

local function drawHealth(o, x0, y0, x1, y1, hp, mx)
    local pct = math.clamp(hp / mx, 0, 1); local bH = y1 - y0
    if bH < 24 then local cy = (y0 + y1) / 2; y0 = cy - 12; y1 = cy + 12; bH = 24 end
    local bX = x0 - 8; local hC = lerpC(ESPS.HealthLow, ESPS.HealthHigh, pct)
    o.HBO.From = Vector2.new(bX, y0 - 1); o.HBO.To = Vector2.new(bX, y1 + 1); o.HBO.Visible = true
    o.HBG.From = Vector2.new(bX, y0); o.HBG.To = Vector2.new(bX, y1); o.HBG.Visible = true
    if pct > 0 then
        o.HB.Color = hC; o.HB.From = Vector2.new(bX, y1); o.HB.To = Vector2.new(bX, y1 - bH * pct); o.HB.Visible = true
    else o.HB.Visible = false end
    o.HT.Text = math.floor(hp) .. "hp"; o.HT.Position = Vector2.new(bX, y0 - 13); o.HT.Visible = true
end

local function drawSnap(o, x0, y0, x1, y1)
    local vp = Camera.ViewportSize
    local orig = ESPS.SnapOrigin == "Bottom" and Vector2.new(vp.X / 2, vp.Y)
        or ESPS.SnapOrigin == "Center" and Vector2.new(vp.X / 2, vp.Y / 2)
        or Vector2.new(vp.X / 2, 0)
    local tgt = Vector2.new((x0 + x1) / 2, y1)
    o.SLO.From = orig; o.SLO.To = tgt; o.SLO.Visible = true
    o.SL.Color = ESPS.SnapColor; o.SL.From = orig; o.SL.To = tgt; o.SL.Visible = true
end

RunService.Heartbeat:Connect(function()
    local now = tick(); if now - ESP_last < ESP_IVL then return end; ESP_last = now
    if not ESPS.Enabled then for _, o in pairs(ESPCache) do hideESP(o) end; return end
    local lc = LocalPlayer.Character
    local lhrp = lc and lc:FindFirstChild("HumanoidRootPart")
    local lpos = lhrp and lhrp.Position
    for pl, o in pairs(ESPCache) do
        if not pl or not pl.Parent then removeESP(pl); continue end
        local char = pl.Character
        local hum = char and char:FindFirstChildOfClass("Humanoid")
        local hrp = char and char:FindFirstChild("HumanoidRootPart")
        if not char or not hum or not hrp then hideESP(o); continue end
        local humHealth = 0; pcall(function() humHealth = hum.Health end)
        if humHealth <= 0 then hideESP(o); continue end
        if ESPS.TeamCheck and pl.Team and LocalPlayer.Team and pl.Team == LocalPlayer.Team then hideESP(o); continue end
        local dist = lpos and (hrp.Position - lpos).Magnitude or 0
        if ESPS.MaxDist > 0 and dist > ESPS.MaxDist then hideESP(o); continue end
        if ESPS.MinDist > 0 and dist < ESPS.MinDist then hideESP(o); continue end
        local sv = Camera:WorldToViewportPoint(hrp.Position)
        if sv.Z <= 0 then hideESP(o); continue end
        local x0, y0, x1, y1 = charBounds(char)
        if not x0 then
            local sp = Vector2.new(sv.X, sv.Y); local fs = math.clamp(200 / math.max(sv.Z, 1), 10, 200)
            x0 = sp.X - fs * 0.5; x1 = sp.X + fs * 0.5; y0 = sp.Y - fs; y1 = sp.Y + fs * 0.5
        end
        local cx = (x0 + x1) / 2
        local humMax = 100; pcall(function() humMax = hum.MaxHealth end)
        if ESPS.Box then drawBox(o, x0, y0, x1, y1) else hideLines(o.BS); hideLines(o.BF) end
        if ESPS.Skeleton then drawSkel(o, char) else
            for i = 1, #o.SK do o.SS[i].Visible = false; o.SK[i].Visible = false end
        end
        if ESPS.HealthBar then
            drawHealth(o, x0, y0, x1, y1, humHealth, humMax)
        else o.HBO.Visible = false; o.HBG.Visible = false; o.HB.Visible = false; o.HT.Visible = false end
        if ESPS.Names then
            o.NL.Color = ESPS.NameColor; o.NL.Text = pl.DisplayName
            o.NL.Position = Vector2.new(cx, y0 - 17); o.NL.Visible = true
        else o.NL.Visible = false end
        if ESPS.Distance then
            o.DL.Color = ESPS.DistColor; o.DL.Text = math.floor(dist) .. "m"
            o.DL.Position = Vector2.new(cx, y1 + 4); o.DL.Visible = true
        else o.DL.Visible = false end
        if ESPS.SnapLines then drawSnap(o, x0, y0, x1, y1) else o.SLO.Visible = false; o.SL.Visible = false end
    end
end)

local function onPlayerAdded(pl)
    createESP(pl)
    pl.CharacterAdded:Connect(function()
        task.wait(0.5); if not ESPCache[pl] then createESP(pl) end
    end)
end
Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(function(pl) removeESP(pl); removeHB(pl) end)
for _, p in ipairs(Players:GetPlayers()) do onPlayerAdded(p) end

local RageBot = {
    Enabled = false, TeamCheck = true, FOVRadius = 120, VisibleCheck = false,
    FireRate = 0.08, lastFire = 0, Status = "IDLE", thread = nil,
    FlyHeight = 30, BV = nil, BG = nil, BP = nil, lastMoverHRP = nil, lockedTarget = nil,
}

local RB_StatusLabel = nil
local RB_FOVCircle = Drawing.new("Circle")
RB_FOVCircle.Visible = false; RB_FOVCircle.Color = Color3.fromRGB(255, 100, 100)
RB_FOVCircle.Thickness = 1.5; RB_FOVCircle.Filled = false
RB_FOVCircle.NumSides = 64; RB_FOVCircle.Transparency = 1
local RB_Conns = {}

local function RB_UpdateStatus(s)
    RageBot.Status = s
    if RB_StatusLabel then pcall(function() RB_StatusLabel:SetText("Status: " .. s) end) end
end

local function RB_IsInMatch()
    local char = LocalPlayer.Character; if not char then return false end
    local hrp = char:FindFirstChild("HumanoidRootPart"); if not hrp then return false end
    local hum = char:FindFirstChildOfClass("Humanoid")
    if not hum or hum.Health <= 0 then return false end
    return true
end

local function RB_GetTarget()
    if RageBot.lockedTarget then
        local pl = RageBot.lockedTarget
        if pl and pl.Parent and pl ~= LocalPlayer then
            local char = pl.Character
            local hum = char and char:FindFirstChildOfClass("Humanoid")
            local head = char and char:FindFirstChild("Head")
            local hrp = char and char:FindFirstChild("HumanoidRootPart")
            if hum and hum.Health > 0 and head and hrp then
                local lc = LocalPlayer.Character
                local lhrp = lc and lc:FindFirstChild("HumanoidRootPart")
                if lhrp and (hrp.Position - lhrp.Position).Magnitude < 5000 then return pl end
            end
        end
        RageBot.lockedTarget = nil
    end
    local best, bestDist = nil, RageBot.FOVRadius
    local center = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
    local lc = LocalPlayer.Character
    local lhrp = lc and lc:FindFirstChild("HumanoidRootPart")
    for _, pl in ipairs(Players:GetPlayers()) do
        if pl == LocalPlayer then continue end
        if RageBot.TeamCheck and pl.Team and LocalPlayer.Team and pl.Team == LocalPlayer.Team then continue end
        local char = pl.Character; if not char then continue end
        local hum = char:FindFirstChildOfClass("Humanoid"); if not hum or hum.Health <= 0 then continue end
        local head = char:FindFirstChild("Head"); if not head then continue end
        local hrp = char:FindFirstChild("HumanoidRootPart"); if not hrp then continue end
        if lhrp and (hrp.Position - lhrp.Position).Magnitude > 5000 then continue end
        if RageBot.VisibleCheck then
            local params = RaycastParams.new()
            params.FilterType = Enum.RaycastFilterType.Blacklist
            params.FilterDescendantsInstances = lc and { lc } or {}
            local res = workspace:Raycast(Camera.CFrame.Position, head.Position - Camera.CFrame.Position, params)
            if res and not res.Instance:IsDescendantOf(char) then continue end
        end
        local sp, on = Camera:WorldToViewportPoint(head.Position)
        if not on or sp.Z <= 0 then continue end
        local dist = (Vector2.new(sp.X, sp.Y) - center).Magnitude
        if dist <= RageBot.FOVRadius and dist < bestDist then bestDist = dist; best = pl end
    end
    if best then RageBot.lockedTarget = best end
    return best
end

local function RB_DestroyMovers()
    if RageBot.BV then pcall(function() RageBot.BV:Destroy() end); RageBot.BV = nil end
    if RageBot.BG then pcall(function() RageBot.BG:Destroy() end); RageBot.BG = nil end
    if RageBot.BP then pcall(function() RageBot.BP:Destroy() end); RageBot.BP = nil end
    RageBot.lastMoverHRP = nil
end

local function RB_AttachMovers(hrp)
    RB_DestroyMovers()
    local bv = Instance.new("BodyVelocity")
    bv.MaxForce = Vector3.new(math.huge, math.huge, math.huge)
    bv.Velocity = Vector3.zero; bv.Name = "RB_BV"
    pcall(function() bv.Parent = hrp end); RageBot.BV = bv
    local bg = Instance.new("BodyGyro")
    bg.MaxTorque = Vector3.new(math.huge, math.huge, math.huge)
    bg.D = 100; bg.P = 10000; bg.CFrame = hrp.CFrame; bg.Name = "RB_BG"
    pcall(function() bg.Parent = hrp end); RageBot.BG = bg
    local bp = Instance.new("BodyPosition")
    bp.MaxForce = Vector3.new(math.huge, math.huge, math.huge)
    bp.P = 500000; bp.D = 5000; bp.Position = hrp.Position; bp.Name = "RB_BP"
    pcall(function() bp.Parent = hrp end); RageBot.BP = bp
    RageBot.lastMoverHRP = hrp
end

local function RB_Stop()
    RageBot.lockedTarget = nil; RB_UpdateStatus("IDLE"); RB_FOVCircle.Visible = false
    if RageBot.thread then task.cancel(RageBot.thread); RageBot.thread = nil end
    for _, c in pairs(RB_Conns) do c:Disconnect() end; RB_Conns = {}
    RB_DestroyMovers()
    local char = LocalPlayer.Character
    local hum = char and char:FindFirstChildOfClass("Humanoid")
    if hum then pcall(function() hum:ChangeState(Enum.HumanoidStateType.GettingUp) end) end
end

local function RB_Start()
    RB_Stop(); RB_UpdateStatus("ACTIVE")
    RB_Conns[1] = RunService.RenderStepped:Connect(function()
        if not RageBot.Enabled then return end
        RB_FOVCircle.Visible = true
        RB_FOVCircle.Position = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
        RB_FOVCircle.Radius = RageBot.FOVRadius
    end)
    RB_Conns[2] = RunService.Heartbeat:Connect(function(dt)
        if not RageBot.Enabled then return end
        if not RB_IsInMatch() then RB_UpdateStatus("NO CHAR"); return end
        local char = LocalPlayer.Character
        local hrp = char and char:FindFirstChild("HumanoidRootPart")
        local hum = char and char:FindFirstChildOfClass("Humanoid")
        if not char or not hrp or not hum then RB_UpdateStatus("NO CHAR"); return end
        if RageBot.lastMoverHRP ~= hrp then RB_AttachMovers(hrp) end
        local target = RB_GetTarget()
        if not target then
            RB_UpdateStatus("NO TARGET")
            if RageBot.BV then pcall(function() RageBot.BV.Velocity = Vector3.zero end) end
            if RageBot.BP then pcall(function() RageBot.BP.Position = hrp.Position end) end
            return
        end
        local tChar = target.Character
        if not tChar then RageBot.lockedTarget = nil; RB_UpdateStatus("NO TARGET"); return end
        local tHRP = tChar:FindFirstChild("HumanoidRootPart")
        if not tHRP then RageBot.lockedTarget = nil; RB_UpdateStatus("NO TARGET"); return end
        pcall(function() hum:ChangeState(Enum.HumanoidStateType.Physics) end)
        local desiredPos
        if RageBot.FlyHeight <= 4 then
            local behindDir = tHRP.CFrame.LookVector * -1
            desiredPos = tHRP.Position + behindDir * 4 + Vector3.new(0, 1, 0)
            RB_UpdateStatus("BEHIND TARGET")
        else
            desiredPos = tHRP.Position + Vector3.new(0, RageBot.FlyHeight, 0)
            RB_UpdateStatus("ABOVE TARGET")
        end
        local toDesired = desiredPos - hrp.Position
        if toDesired.Magnitude > 0.5 then
            pcall(function() hrp.CFrame = CFrame.new(desiredPos) end)
            if RageBot.BP then pcall(function() RageBot.BP.Position = desiredPos end) end
            if RageBot.BV then pcall(function() RageBot.BV.Velocity = Vector3.zero end) end
        else
            if RageBot.BV then pcall(function() RageBot.BV.Velocity = Vector3.zero end) end
            if RageBot.BP then pcall(function() RageBot.BP.Position = desiredPos end) end
        end
        local lookDir = tHRP.Position - hrp.Position
        if lookDir.Magnitude > 0.1 and RageBot.BG then
            pcall(function() RageBot.BG.CFrame = CFrame.lookAt(hrp.Position, tHRP.Position) end)
        end
    end)
    RageBot.thread = task.spawn(function()
        while RageBot.Enabled do
            if not RB_IsInMatch() then task.wait(0.1); continue end
            local target = RB_GetTarget()
            if target then
                local tChar = target.Character
                local head = tChar and tChar:FindFirstChild("Head")
                if head then
                    Camera.CFrame = CFrame.new(Camera.CFrame.Position, head.Position)
                    local sp = Camera:WorldToViewportPoint(head.Position)
                    local center = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
                    local dx = sp.X - center.X; local dy = sp.Y - center.Y
                    if math.abs(dx) > 0.5 or math.abs(dy) > 0.5 then
                        pcall(function() mousemoverel(dx, dy) end)
                    end
                    pcall(function() ReplicatedStorage.Remotes.Attack:FireServer(head) end)
                    pcall(function() mouse1click() end)
                    RageBot.lastFire = tick(); task.wait(RageBot.FireRate)
                else task.wait(0.05) end
            else task.wait(0.05) end
        end
    end)
end

LocalPlayer.CharacterAdded:Connect(function()
    task.wait(0.8)
    if RageBot.Enabled then RageBot.lockedTarget = nil; RB_DestroyMovers(); RB_Start() end
end)

local Matchmaking = { Enabled = false, Selected = "2v2" }

local function MM_JoinQueue()
    if not Matchmaking.Enabled then return end
    task.spawn(function()
        local ok, err = pcall(function()
            ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("Matchmaking"):WaitForChild("JoinQueue"):InvokeServer(Matchmaking.Selected)
        end)
        if ok then
            Library:Notify({ Title = "Matchmaking", Description = "Joined queue: " .. Matchmaking.Selected, Time = 3 })
        else
            Library:Notify({ Title = "Matchmaking", Description = "Failed: " .. tostring(err):sub(1, 60), Time = 4 })
        end
    end)
end

local function doUnlock()
    Library:Notify({ Title = "Unlock All", Description = "Unlocking cosmetics...", Time = 3 })
    task.defer(function()
        local ok, err = pcall(function()
            local playerScripts = LocalPlayer.PlayerScripts
            local controllers = playerScripts.Controllers
            local CosmeticLibrary = require(ReplicatedStorage.Modules:WaitForChild("CosmeticLibrary", 10))
            local DataController = require(controllers:WaitForChild("PlayerDataController", 10))
            CosmeticLibrary.OwnsCosmeticNormally = function() return true end
            CosmeticLibrary.OwnsCosmeticUniversally = function() return true end
            CosmeticLibrary.OwnsCosmeticForWeapon = function() return true end
            local originalOwnsCosmetic = CosmeticLibrary.OwnsCosmetic
            CosmeticLibrary.OwnsCosmetic = function(self, inventory, name, weapon)
                if type(name) == "string" and name:find("MISSING_") then
                    return originalOwnsCosmetic(self, inventory, name, weapon)
                end
                return true
            end
            local originalGet = DataController.Get
            DataController.Get = function(self, key)
                local data = originalGet(self, key)
                if key == "CosmeticInventory" then
                    local proxy = {}
                    if data then for k, v in pairs(data) do proxy[k] = v end end
                    return setmetatable(proxy, { __index = function() return true end })
                end
                return data
            end
        end)
        if ok then
            Library:Notify({ Title = "Unlock All", Description = "Cosmetics unlocked!", Time = 5 })
        else
            Library:Notify({ Title = "Unlock All", Description = "Failed: " .. tostring(err):sub(1, 60), Time = 6 })
        end
    end)
end

local DeviceSpoof = { Enabled = false, Selected = "Computer" }
local deviceSpoofMap = { Computer = "MouseKeyboard", Mobile = "Touch", Console = "Gamepad", VR = "VR" }

local function applySpoofs()
    if not DeviceSpoof.Enabled then return end
    task.spawn(function()
        local remote = nil
        pcall(function()
            local rem = ReplicatedStorage:FindFirstChild("Remotes"); if not rem then return end
            local rep = rem:FindFirstChild("Replication"); if not rep then return end
            local fig = rep:FindFirstChild("Fighter"); if not fig then return end
            remote = fig:FindFirstChild("SetControls")
        end)
        if not remote then Library:Notify({ Title = "Device Spoofer", Description = "Remote not found", Time = 4 }); return end
        local t = deviceSpoofMap[DeviceSpoof.Selected]
        if t then
            pcall(function() remote:FireServer(t) end)
            Library:Notify({ Title = "Device Spoofer", Description = "Spoofed as: " .. DeviceSpoof.Selected, Time = 3 })
        end
    end)
end


do
    local CHEffect = { Mode = "Default", t = 0, BaseColor = Color3.fromRGB(255, 255, 255) }

    local function HSVtoRGB(h, s, v)
        local r, g, b
        local i = math.floor(h * 6); local f = h * 6 - i; local p = v * (1 - s)
        local q = v * (1 - f * s); local t_ = v * (1 - (1 - f) * s); local mod = i % 6
        if mod == 0 then r, g, b = v, t_, p elseif mod == 1 then r, g, b = q, v, p
        elseif mod == 2 then r, g, b = p, v, t_ elseif mod == 3 then r, g, b = p, q, v
        elseif mod == 4 then r, g, b = t_, p, v elseif mod == 5 then r, g, b = v, p, q end
        return Color3.new(r, g, b)
    end

    local function getEffectColor(dt)
        CHEffect.t = CHEffect.t + dt; local t = CHEffect.t; local mode = CHEffect.Mode
        if mode == "Default" then return CHEffect.BaseColor
        elseif mode == "Rainbow" then return HSVtoRGB((t * 0.18) % 1, 1, 1)
        elseif mode == "Pulse Rainbow" then return HSVtoRGB((t * 0.2) % 1, 1, 0.7 + math.sin(t * 4) * 0.3)
        elseif mode == "Neon Flicker" then
            local fl = math.random() > 0.05 and 1 or 0.3
            return HSVtoRGB(0.7 + math.sin(t * 2) * 0.05, 0.8, fl)
        elseif mode == "Fire" then
            local ph = (math.sin(t * 5) + 1) / 2
            return ph < 0.5 and lerpC(Color3.fromRGB(255, 0, 0), Color3.fromRGB(255, 120, 0), ph * 2)
                or lerpC(Color3.fromRGB(255, 120, 0), Color3.fromRGB(255, 255, 0), (ph - 0.5) * 2)
        elseif mode == "Ocean Wave" then
            local ph = (math.sin(t * 2.5) + 1) / 2
            return ph < 0.5 and lerpC(Color3.fromRGB(0, 200, 255), Color3.fromRGB(0, 80, 255), ph * 2)
                or lerpC(Color3.fromRGB(0, 80, 255), Color3.fromRGB(0, 220, 180), (ph - 0.5) * 2)
        elseif mode == "Synthwave" then
            local ph = (t * 0.3) % 1
            if ph < 0.33 then return lerpC(Color3.fromRGB(255, 0, 180), Color3.fromRGB(150, 0, 255), ph / 0.33)
            elseif ph < 0.66 then return lerpC(Color3.fromRGB(150, 0, 255), Color3.fromRGB(0, 220, 255), (ph - 0.33) / 0.33)
            else return lerpC(Color3.fromRGB(0, 220, 255), Color3.fromRGB(255, 0, 180), (ph - 0.66) / 0.34) end
        elseif mode == "Gold Shimmer" then
            local sh = 0.75 + math.sin(t * 8 + math.sin(t * 3)) * 0.25
            return lerpC(Color3.fromRGB(200, 140, 0), Color3.fromRGB(255, 230, 80), sh)
        elseif mode == "Blood Moon" then
            local pulse = 0.6 + math.sin(t * 3) * 0.4
            return lerpC(Color3.fromRGB(80, 0, 0), Color3.fromRGB(255, 30, 30), pulse)
        elseif mode == "Matrix" then
            local fl = (math.sin(t * 20) > 0.3) and 1 or 0.4; return Color3.new(0, fl, 0)
        end
        return CHEffect.BaseColor
    end

    local CHGui = Instance.new("ScreenGui")
    CHGui.Name = "CrosshairSystem"; CHGui.ResetOnSpawn = false; CHGui.IgnoreGuiInset = true
    CHGui.DisplayOrder = 999999; CHGui.Parent = PGui

    local CH = {
        Enabled = true, Color = Color3.fromRGB(255, 255, 255), baseGap = 10, Gap = 10,
        Thick = 2, Len = 10, Len2 = 20, Dot = 4, Style = "Cross", Anim = {}, SpinI = 1, PulseI = 1,
        t = 0, pos = Vector2.new(0.5, 0.5), lastOvr = 0, spinAngle = 0, BrandingVisible = true
    }

    local chH = Instance.new("Frame"); chH.Size = UDim2.new(0, 120, 0, 120)
    chH.AnchorPoint = Vector2.new(0.5, 0.5); chH.BackgroundTransparency = 1; chH.Parent = CHGui

    
    local brandHolder = Instance.new("Frame"); brandHolder.Name = "CrystalizedBrand"
    brandHolder.Size = UDim2.new(0, 130, 0, 18); brandHolder.AnchorPoint = Vector2.new(0.5, 0)
    brandHolder.BackgroundTransparency = 1; brandHolder.ZIndex = 10; brandHolder.Parent = CHGui
    brandHolder.Visible = true 

    local diamond = Instance.new("Frame"); diamond.Name = "Diamond"
    diamond.Size = UDim2.new(0, 7, 0, 7); diamond.AnchorPoint = Vector2.new(0.5, 0.5)
    diamond.Position = UDim2.new(0, 9, 0.5, 0); diamond.Rotation = 45; diamond.BorderSizePixel = 0
    diamond.BackgroundColor3 = Color3.fromRGB(255, 255, 255); diamond.ZIndex = 11; diamond.Parent = brandHolder

    local dGrad = Instance.new("UIGradient", diamond)
    dGrad.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 255, 255)),
        ColorSequenceKeypoint.new(0.5, Color3.fromRGB(210, 240, 255)),
        ColorSequenceKeypoint.new(1, Color3.fromRGB(255, 255, 255))
    }); dGrad.Rotation = 45

    local brandLabel = Instance.new("TextLabel"); brandLabel.Name = "BrandText"
    brandLabel.Size = UDim2.new(1, -16, 1, 0); brandLabel.Position = UDim2.new(0, 16, 0, 0)
    brandLabel.BackgroundTransparency = 1; brandLabel.Text = "discord.gg/crystalized"
    brandLabel.Font = Enum.Font.GothamBold; brandLabel.TextSize = 10
    brandLabel.TextXAlignment = Enum.TextXAlignment.Left
    brandLabel.TextYAlignment = Enum.TextYAlignment.Center
    brandLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    brandLabel.TextStrokeTransparency = 0.3; brandLabel.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
    brandLabel.ZIndex = 11; brandLabel.Parent = brandHolder

    local tGrad = Instance.new("UIGradient", brandLabel)
    tGrad.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 255, 255)),
        ColorSequenceKeypoint.new(0.4, Color3.fromRGB(200, 235, 255)),
        ColorSequenceKeypoint.new(0.6, Color3.fromRGB(255, 255, 255)),
        ColorSequenceKeypoint.new(1, Color3.fromRGB(220, 245, 255))
    })

    local brandT = 0
    RunService.RenderStepped:Connect(function(dt)
        brandT = brandT + dt * 0.5
        
        if brandHolder.Visible then
            local off = math.sin(brandT) * 0.35
            tGrad.Offset = Vector2.new(off, 0); dGrad.Offset = Vector2.new(off * 0.4, 0)
            local vp = Camera.ViewportSize
            brandHolder.Position = UDim2.new(0, CH.pos.X * vp.X, 0, CH.pos.Y * vp.Y + 30)
        end
    end)

    local cU, cD, cL, cR, cSq, cSt, cDot

    local function syncColor(col)
        col = col or CH.Color
        for _, v in ipairs(chH:GetDescendants()) do
            if v:IsA("Frame") then v.BackgroundColor3 = col end
            if v:IsA("UIStroke") then v.Color = col end
        end
        if cSt then cSt.TextColor3 = col end
    end

    local function chDot()
        cDot = Instance.new("Frame"); cDot.Size = UDim2.new(0, CH.Dot, 0, CH.Dot)
        cDot.AnchorPoint = Vector2.new(0.5, 0.5); cDot.Position = UDim2.new(0.5, 0, 0.5, 0)
        cDot.BorderSizePixel = 0; cDot.BackgroundColor3 = CH.Color; cDot.Parent = chH
        Instance.new("UICorner", cDot).CornerRadius = UDim.new(1, 0)
    end

    local function chCross()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        cU = Instance.new("Frame"); cU.BorderSizePixel = 0; cU.AnchorPoint = Vector2.new(0.5, 0.5)
        cU.Size = UDim2.new(0, CH.Thick, 0, CH.Len); cU.BackgroundColor3 = CH.Color; cU.Parent = chH
        cD = cU:Clone(); cD.Parent = chH
        cL = Instance.new("Frame"); cL.BorderSizePixel = 0; cL.AnchorPoint = Vector2.new(0.5, 0.5)
        cL.Size = UDim2.new(0, CH.Len, 0, CH.Thick); cL.BackgroundColor3 = CH.Color; cL.Parent = chH
        cR = cL:Clone(); cR.Parent = chH; chDot()
    end
    local function chSquare()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        cSq = Instance.new("Frame"); cSq.Size = UDim2.new(0, CH.Len2, 0, CH.Len2)
        cSq.Position = UDim2.new(0.5, 0, 0.5, 0); cSq.AnchorPoint = Vector2.new(0.5, 0.5)
        cSq.BackgroundTransparency = 1; cSq.Parent = chH
        local st = Instance.new("UIStroke", cSq); st.Thickness = CH.Thick; st.Color = CH.Color; chDot()
    end
    local function chStar()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        cSt = Instance.new("TextLabel"); cSt.Size = UDim2.new(0, CH.Len2, 0, CH.Len2)
        cSt.Position = UDim2.new(0.5, 0, 0.5, 0); cSt.AnchorPoint = Vector2.new(0.5, 0.5)
        cSt.BackgroundTransparency = 1; cSt.Text = "★"; cSt.TextScaled = true
        cSt.Font = Enum.Font.GothamBlack; cSt.TextColor3 = CH.Color; cSt.Parent = chH
    end
    local function chTShape()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        cL = Instance.new("Frame"); cL.BorderSizePixel = 0; cL.AnchorPoint = Vector2.new(1, 0.5)
        cL.Size = UDim2.new(0, CH.Len, 0, CH.Thick); cL.BackgroundColor3 = CH.Color; cL.Parent = chH
        cR = Instance.new("Frame"); cR.BorderSizePixel = 0; cR.AnchorPoint = Vector2.new(0, 0.5)
        cR.Size = UDim2.new(0, CH.Len, 0, CH.Thick); cR.BackgroundColor3 = CH.Color; cR.Parent = chH
        cD = Instance.new("Frame"); cD.BorderSizePixel = 0; cD.AnchorPoint = Vector2.new(0.5, 0)
        cD.Size = UDim2.new(0, CH.Thick, 0, CH.Len); cD.BackgroundColor3 = CH.Color; cD.Parent = chH
    end
    local function chCircle()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        cSq = Instance.new("Frame"); cSq.Size = UDim2.new(0, CH.Len2, 0, CH.Len2)
        cSq.Position = UDim2.new(0.5, 0, 0.5, 0); cSq.AnchorPoint = Vector2.new(0.5, 0.5)
        cSq.BackgroundTransparency = 1; cSq.Parent = chH
        Instance.new("UICorner", cSq).CornerRadius = UDim.new(1, 0)
        local st = Instance.new("UIStroke", cSq); st.Thickness = CH.Thick; st.Color = CH.Color; chDot()
    end
    local function chArrow()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        local function mkArm(px, rot)
            local f = Instance.new("Frame"); f.BorderSizePixel = 0
            f.AnchorPoint = Vector2.new(0.5, 1); f.Size = UDim2.new(0, CH.Thick, 0, CH.Len)
            f.Rotation = rot; f.BackgroundColor3 = CH.Color
            f.Position = UDim2.new(0.5, px, 0.5, 0); f.Parent = chH
        end
        mkArm(-CH.Len * 0.4, -35); mkArm(CH.Len * 0.4, 35); chDot()
    end
    local function chX()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        local a1 = Instance.new("Frame"); a1.BorderSizePixel = 0; a1.AnchorPoint = Vector2.new(0.5, 0.5)
        a1.Size = UDim2.new(0, CH.Thick, 0, CH.Len * 1.4); a1.Rotation = 45
        a1.BackgroundColor3 = CH.Color; a1.Position = UDim2.new(0.5, 0, 0.5, 0); a1.Parent = chH
        local a2 = a1:Clone(); a2.Rotation = -45; a2.Parent = chH; chDot()
    end
    local function chDotOnly()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        local sz = math.max(CH.Dot * 2, 6)
        cDot = Instance.new("Frame"); cDot.Size = UDim2.new(0, sz, 0, sz)
        cDot.AnchorPoint = Vector2.new(0.5, 0.5); cDot.Position = UDim2.new(0.5, 0, 0.5, 0)
        cDot.BorderSizePixel = 0; cDot.BackgroundColor3 = CH.Color; cDot.Parent = chH
        Instance.new("UICorner", cDot).CornerRadius = UDim.new(1, 0)
    end
    local function chTactical()
        chH:ClearAllChildren(); cDot = nil; cSq = nil; cSt = nil
        local function mkBracket(px, py, w, h)
            local f = Instance.new("Frame"); f.BorderSizePixel = 0
            f.AnchorPoint = Vector2.new(0.5, 0.5); f.Size = UDim2.new(0, w, 0, h)
            f.Position = UDim2.new(0.5, px, 0.5, py); f.BackgroundColor3 = CH.Color; f.Parent = chH
        end
        local g, tl = CH.Gap, CH.Len * 0.5
        mkBracket(-(g + tl / 2), -(g), tl, CH.Thick); mkBracket(-(g), -(g + tl / 2), CH.Thick, tl)
        mkBracket((g + tl / 2), -(g), tl, CH.Thick); mkBracket((g), -(g + tl / 2), CH.Thick, tl)
        mkBracket(-(g + tl / 2), (g), tl, CH.Thick); mkBracket(-(g), (g + tl / 2), CH.Thick, tl)
        mkBracket((g + tl / 2), (g), tl, CH.Thick); mkBracket((g), (g + tl / 2), CH.Thick, tl); chDot()
    end

    local function applyStyle()
        CH.spinAngle = 0; chH.Rotation = 0
        if CH.Style == "Cross" then chCross()
        elseif CH.Style == "Square" then chSquare()
        elseif CH.Style == "Star" then chStar()
        elseif CH.Style == "T-Shape" then chTShape()
        elseif CH.Style == "Circle" then chCircle()
        elseif CH.Style == "Arrow" then chArrow()
        elseif CH.Style == "X" then chX()
        elseif CH.Style == "Dot Only" then chDotOnly()
        elseif CH.Style == "Tactical" then chTactical() end
    end
    applyStyle()

    local function updTShape()
        if not cL or not cR or not cD then return end
        cL.Position = UDim2.new(0.5, -CH.Gap, 0.5, -CH.Gap)
        cR.Position = UDim2.new(0.5, CH.Gap, 0.5, -CH.Gap)
        cD.Position = UDim2.new(0.5, 0, 0.5, CH.Gap)
    end
    local function updCross()
        if not cU then return end
        cU.Position = UDim2.new(0.5, 0, 0.5, -CH.Gap)
        cD.Position = UDim2.new(0.5, 0, 0.5, CH.Gap)
        cL.Position = UDim2.new(0.5, -CH.Gap, 0.5, 0)
        cR.Position = UDim2.new(0.5, CH.Gap, 0.5, 0)
    end

    local function ovrInterfaces()
        local now = os.clock(); if now - CH.lastOvr < 0.5 then return end; CH.lastOvr = now
        local mg = PGui:FindFirstChild("MainGui"); if not mg then return end
        local mf = mg:FindFirstChild("MainFrame"); if not mf then return end
        local ii = mf:FindFirstChild("ItemInterfaces"); if not ii then return end
        local found = false
        for _, v in ipairs(ii:GetDescendants()) do
            if v:IsA("GuiObject") then
                if v.Name:lower():find("crosshair") then
                    local ap = v.AbsolutePosition; local as = v.AbsoluteSize; local ss = Camera.ViewportSize
                    CH.pos = Vector2.new((ap.X + as.X / 2) / ss.X, (ap.Y + as.Y / 2) / ss.Y); found = true
                end
                v:Destroy()
            end
        end
        if not found then CH.pos = Vector2.new(0.5, 0.5) end
    end

    RunService.RenderStepped:Connect(function(dt)
        if not CH.Enabled then chH.Visible = false; return end
        chH.Visible = true; ovrInterfaces()
        local vp = Camera.ViewportSize; chH.Position = UDim2.new(0, CH.pos.X * vp.X, 0, CH.pos.Y * vp.Y)
        local effectColor = getEffectColor(dt)
        local activeColor = CHEffect.Mode == "Default" and CH.Color or effectColor
        if activeColor ~= CH.Color or CHEffect.Mode ~= "Default" then syncColor(activeColor) end
        local ps = 1
        if table.find(CH.Anim, "Pulse") then
            CH.t += dt * (6 * CH.PulseI); CH.Gap = CH.baseGap + math.sin(CH.t) * (4 * CH.PulseI)
            ps = 1 + math.sin(tick() * 6) * 0.15 * CH.PulseI
        else CH.Gap = CH.baseGap end
        if cDot then cDot.Size = UDim2.new(0, CH.Dot * ps, 0, CH.Dot * ps) end
        local doSpin = table.find(CH.Anim, "Spin")
        if doSpin then CH.spinAngle = CH.spinAngle + dt * (180 * CH.SpinI) end
        if CH.Style == "Cross" then
            updCross(); chH.Rotation = doSpin and CH.spinAngle or 0
            if cU then cU.Size = UDim2.new(0, CH.Thick, 0, CH.Len * ps); cD.Size = UDim2.new(0, CH.Thick, 0, CH.Len * ps) end
            if cL then cL.Size = UDim2.new(0, CH.Len * ps, 0, CH.Thick); cR.Size = UDim2.new(0, CH.Len * ps, 0, CH.Thick) end
        elseif CH.Style == "Square" then
            chH.Rotation = doSpin and CH.spinAngle or 0
            if cSq then local sz = CH.Len2 * ps; cSq.Size = UDim2.new(0, sz, 0, sz) end
        elseif CH.Style == "Star" then
            if cSt then if doSpin then cSt.Rotation = CH.spinAngle end
                local sz = CH.Len2 * ps; cSt.Size = UDim2.new(0, sz, 0, sz) end; chH.Rotation = 0
        elseif CH.Style == "T-Shape" then
            updTShape(); chH.Rotation = doSpin and CH.spinAngle or 0
        elseif CH.Style == "Circle" then
            chH.Rotation = doSpin and CH.spinAngle or 0
            if cSq then local sz = CH.Len2 * ps; cSq.Size = UDim2.new(0, sz, 0, sz) end
        elseif CH.Style == "Dot Only" then
            chH.Rotation = 0
            if cDot then local sz = math.max(CH.Dot * 2, 6) * ps; cDot.Size = UDim2.new(0, sz, 0, sz) end
        else chH.Rotation = doSpin and CH.spinAngle or 0 end
        if PS.NoclipEnabled then setCollision(false) end
    end)


    local origLighting = {
        Brightness = Lighting.Brightness, FogColor = Lighting.FogColor,
        FogStart = Lighting.FogStart, FogEnd = Lighting.FogEnd,
        Ambient = Lighting.Ambient, OutdoorAmbient = Lighting.OutdoorAmbient,
        TimeOfDay = Lighting.TimeOfDay
    }
    local WE = {
        SkyEnabled = false, SkyColor = Color3.fromRGB(30, 60, 120),
        AmbientColor = Color3.fromRGB(70, 70, 70), OutdoorAmbient = Color3.fromRGB(100, 100, 140),
        BrightnessEnabled = false, Brightness = 1, FogEnabled = false,
        FogColor = Color3.fromRGB(180, 200, 220), FogStart = 0, FogEnd = 300,
        BloomEnabled = false, BloomIntensity = 0.5, BloomSize = 24, BloomThreshold = 0.95,
        BlurEnabled = false, BlurSize = 8, CCEnabled = false, CCBrightness = 0, CCContrast = 0,
        CCSaturation = 0, CCTintColor = Color3.fromRGB(255, 255, 255),
        DOFEnabled = false, DOFFarIntensity = 1, DOFFocusDistance = 50, DOFInFocusRadius = 10, DOFNearIntensity = 1,
        SunRaysEnabled = false, SunRaysIntensity = 0.1, SunRaysSpread = 0.5,
        SnowEnabled = false, SnowSpeed = 1, SnowDensity = 200, SnowSize = 0.3, SnowColor = Color3.fromRGB(255, 255, 255),
        RainEnabled = false, RainSpeed = 3, RainDensity = 300, TimeEnabled = false, TimeOfDay = 14
    }

    local function getOrCreate(cls, name)
        local e = Lighting:FindFirstChild(name)
        if e and e.ClassName == cls then return e end
        if e then e:Destroy() end
        local i = Instance.new(cls); i.Name = name; i.Parent = Lighting; return i
    end
    local function destroyNamed(name) local e = Lighting:FindFirstChild(name); if e then e:Destroy() end end
    local function applySkyClock() Lighting.Ambient = WE.AmbientColor; Lighting.OutdoorAmbient = WE.OutdoorAmbient end
    local function removeSky() Lighting.Ambient = origLighting.Ambient; Lighting.OutdoorAmbient = origLighting.OutdoorAmbient end
    local function applyBrightness() Lighting.Brightness = WE.BrightnessEnabled and WE.Brightness or origLighting.Brightness end
    local function applyFog()
        if WE.FogEnabled then
            Lighting.FogColor = WE.FogColor; Lighting.FogStart = WE.FogStart; Lighting.FogEnd = WE.FogEnd
        else Lighting.FogColor = origLighting.FogColor; Lighting.FogStart = origLighting.FogStart; Lighting.FogEnd = origLighting.FogEnd end
    end
    local function applyBloom()
        if WE.BloomEnabled then
            local b = getOrCreate("BloomEffect", "WE_Bloom"); b.Intensity = WE.BloomIntensity
            b.Size = WE.BloomSize; b.Threshold = WE.BloomThreshold; b.Enabled = true
        else destroyNamed("WE_Bloom") end
    end
    local function applyBlur()
        if WE.BlurEnabled then
            local b = getOrCreate("BlurEffect", "WE_Blur"); b.Size = WE.BlurSize; b.Enabled = true
        else destroyNamed("WE_Blur") end
    end
    local function applyCC()
        if WE.CCEnabled then
            local c = getOrCreate("ColorCorrectionEffect", "WE_CC")
            c.Brightness = WE.CCBrightness; c.Contrast = WE.CCContrast
            c.Saturation = WE.CCSaturation; c.TintColor = WE.CCTintColor; c.Enabled = true
        else destroyNamed("WE_CC") end
    end
    local function applyDOF()
        if WE.DOFEnabled then
            local d = getOrCreate("DepthOfFieldEffect", "WE_DOF")
            d.FarIntensity = WE.DOFFarIntensity; d.FocusDistance = WE.DOFFocusDistance
            d.InFocusRadius = WE.DOFInFocusRadius; d.NearIntensity = WE.DOFNearIntensity; d.Enabled = true
        else destroyNamed("WE_DOF") end
    end
    local function applySunRays()
        if WE.SunRaysEnabled then
            local s = getOrCreate("SunRaysEffect", "WE_SunRays")
            s.Intensity = WE.SunRaysIntensity; s.Spread = WE.SunRaysSpread; s.Enabled = true
        else destroyNamed("WE_SunRays") end
    end
    local function applyTime()
        if WE.TimeEnabled then
            local h = math.floor(WE.TimeOfDay); local m = math.floor((WE.TimeOfDay - h) * 60)
            Lighting.TimeOfDay = string.format("%02d:%02d:00", h, m)
        else Lighting.TimeOfDay = origLighting.TimeOfDay end
    end

    local snowFolder, snowPart, snowEmitter, snowMoveConn = nil, nil, nil, nil
    local function clearSnow()
        WE.SnowEnabled = false
        if snowMoveConn then snowMoveConn:Disconnect(); snowMoveConn = nil end
        if snowFolder then pcall(function() snowFolder:Destroy() end); snowFolder = nil end
        snowPart = nil; snowEmitter = nil
    end
    local function buildSnow()
        clearSnow(); WE.SnowEnabled = true
        local char = LocalPlayer.Character
        local hrp = char and char:FindFirstChild("HumanoidRootPart"); if not hrp then return end
        snowFolder = Instance.new("Folder"); snowFolder.Name = "WE_SnowFolder"; snowFolder.Parent = workspace
        snowPart = Instance.new("Part"); snowPart.Name = "WE_SnowEmitter"
        snowPart.Size = Vector3.new(60, 1, 60); snowPart.CFrame = hrp.CFrame * CFrame.new(0, 20, 0)
        snowPart.Anchored = true; snowPart.CanCollide = false; snowPart.Transparency = 1
        snowPart.CastShadow = false; snowPart.Parent = snowFolder
        snowEmitter = Instance.new("ParticleEmitter"); snowEmitter.Name = "WE_Snow"
        snowEmitter.Texture = "rbxassetid://6914281109"; snowEmitter.Color = ColorSequence.new(WE.SnowColor)
        snowEmitter.LightEmission = 0; snowEmitter.LightInfluence = 1
        snowEmitter.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, WE.SnowSize), NumberSequenceKeypoint.new(1, WE.SnowSize * 0.5) })
        snowEmitter.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(0.8, 0.3), NumberSequenceKeypoint.new(1, 1) })
        snowEmitter.Speed = NumberRange.new(3 * WE.SnowSpeed, 7 * WE.SnowSpeed)
        snowEmitter.Rate = WE.SnowDensity; snowEmitter.Lifetime = NumberRange.new(4, 7)
        snowEmitter.Rotation = NumberRange.new(0, 360); snowEmitter.RotSpeed = NumberRange.new(-30, 30)
        snowEmitter.SpreadAngle = Vector2.new(25, 25); snowEmitter.VelocityInheritance = 0
        snowEmitter.Parent = snowPart
        snowMoveConn = RunService.Heartbeat:Connect(function()
            if not WE.SnowEnabled then return end
            local c = LocalPlayer.Character; local rp = c and c:FindFirstChild("HumanoidRootPart")
            if rp and snowPart and snowPart.Parent then snowPart.CFrame = CFrame.new(rp.Position + Vector3.new(0, 20, 0)) end
        end)
    end
    LocalPlayer.CharacterAdded:Connect(function() task.wait(1); if WE.SnowEnabled then buildSnow() end end)

    local rainFolder, rainPart, rainEmitter, rainMoveConn = nil, nil, nil, nil
    local function clearRain()
        WE.RainEnabled = false
        if rainMoveConn then rainMoveConn:Disconnect(); rainMoveConn = nil end
        if rainFolder then pcall(function() rainFolder:Destroy() end); rainFolder = nil end
        rainPart = nil; rainEmitter = nil
    end
    local function buildRain()
        clearRain(); WE.RainEnabled = true
        local char = LocalPlayer.Character
        local hrp = char and char:FindFirstChild("HumanoidRootPart"); if not hrp then return end
        rainFolder = Instance.new("Folder"); rainFolder.Name = "WE_RainFolder"; rainFolder.Parent = workspace
        rainPart = Instance.new("Part"); rainPart.Name = "WE_RainEmitter"
        rainPart.Size = Vector3.new(70, 1, 70); rainPart.CFrame = hrp.CFrame * CFrame.new(0, 25, 0)
        rainPart.Anchored = true; rainPart.CanCollide = false; rainPart.Transparency = 1
        rainPart.CastShadow = false; rainPart.Parent = rainFolder
        rainEmitter = Instance.new("ParticleEmitter"); rainEmitter.Name = "WE_Rain"
        rainEmitter.Texture = "rbxassetid://6884282101"
        rainEmitter.Color = ColorSequence.new(Color3.fromRGB(180, 210, 255))
        rainEmitter.LightEmission = 0; rainEmitter.LightInfluence = 1
        rainEmitter.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.04), NumberSequenceKeypoint.new(1, 0.04) })
        rainEmitter.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(0.9, 0.4), NumberSequenceKeypoint.new(1, 1) })
        rainEmitter.Speed = NumberRange.new(28 * WE.RainSpeed, 40 * WE.RainSpeed)
        rainEmitter.Rate = WE.RainDensity; rainEmitter.Lifetime = NumberRange.new(0.6, 1.2)
        rainEmitter.Rotation = NumberRange.new(0, 0); rainEmitter.RotSpeed = NumberRange.new(0, 0)
        rainEmitter.SpreadAngle = Vector2.new(4, 4); rainEmitter.VelocityInheritance = 0
        rainEmitter.Parent = rainPart
        rainMoveConn = RunService.Heartbeat:Connect(function()
            if not WE.RainEnabled then return end
            local c = LocalPlayer.Character; local rp = c and c:FindFirstChild("HumanoidRootPart")
            if rp and rainPart and rainPart.Parent then rainPart.CFrame = CFrame.new(rp.Position + Vector3.new(0, 25, 0)) end
        end)
    end
    LocalPlayer.CharacterAdded:Connect(function() task.wait(1); if WE.RainEnabled then buildRain() end end)



    local function buildFighting()
        local FL = Tabs.Fighting:AddLeftGroupbox("Silent Aim")
        local FA = Tabs.Fighting:AddLeftGroupbox("Aimbot")
        local FR = Tabs.Fighting:AddRightGroupbox("Auto Shoot")
        local FU = Tabs.Fighting:AddRightGroupbox("Utilities")
        local FAG = Tabs.Fighting:AddRightGroupbox("Anti Gadgets")
        local FMM = Tabs.Fighting:AddRightGroupbox("Matchmaking")

        FL:AddToggle("SilentAim", { Text = "Silent Aim", Default = false, Callback = function(v) SA.enabled = v; if v then SA_start() else SA_stop() end end })
        FL:AddToggle("SAVisCheck", { Text = "Visible Check", Default = false, Callback = function(v) SA.visibleCheck = v end })
        FL:AddSlider("SAFov", { Text = "FOV Radius", Default = 70, Min = 20, Max = 300, Rounding = 0, Callback = function(v) SA.FOVRadius = v end })
        local saFC = FL:AddLabel("FOV Circle Color"); saFC:AddColorPicker("SAFovCol", { Default = Color3.fromRGB(255, 255, 255), Title = "SA FOV", Callback = function(v) SA_FOV.Color = v end })
        local saKB = FL:AddLabel("Toggle Keybind"); saKB:AddKeyPicker("SAKeybind", { Default = "None", Mode = "Toggle", Text = "Silent Aim", NoUI = false, Callback = function(s) Toggles.SilentAim:SetValue(s); if s then SA_start() else SA_stop() end end })

        FA:AddToggle("AimbotEnabled", { Text = "Aimbot (hold RMB)", Default = false, Callback = function(v) Aimbot.Enabled = v; if v then Ab_Start() else Ab_Stop() end end })
        FA:AddSlider("AbFov", { Text = "FOV Radius", Default = 150, Min = 20, Max = 500, Rounding = 0, Callback = function(v) Aimbot.FOVRadius = v end })
        FA:AddSlider("AbSmooth", { Text = "Smoothing", Default = 5, Min = 1, Max = 50, Rounding = 1, Callback = function(v) Aimbot.Smoothing = v end })
        FA:AddSlider("AbPred", { Text = "Prediction", Default = 0, Min = 0, Max = 0.5, Rounding = 2, Callback = function(v) Aimbot.Prediction = v end })
        FA:AddSlider("AbHit", { Text = "Hit Chance (%)", Default = 100, Min = 1, Max = 100, Rounding = 0, Callback = function(v) Aimbot.HitChance = v end })
        FA:AddToggle("AbVis", { Text = "Visible Check", Default = false, Callback = function(v) Aimbot.VisibleCheck = v end })
        FA:AddToggle("AbTeam", { Text = "Team Check", Default = false, Callback = function(v) Aimbot.TeamCheck = v end })
        FA:AddDropdown("AbPart", { Text = "Target Part", Values = { "Head", "UpperTorso", "LowerTorso", "HumanoidRootPart" }, Default = "Head", Multi = false, Callback = function(v) Aimbot.TargetPart = v end })
        local abFC = FA:AddLabel("FOV Circle Color"); abFC:AddColorPicker("AbFovCol", { Default = Color3.fromRGB(255, 255, 255), Title = "Aimbot FOV", Callback = function(v) AbFOV.Color = v end })
        local abKB = FA:AddLabel("Toggle Keybind"); abKB:AddKeyPicker("AbKeybind", { Default = "None", Mode = "Toggle", Text = "Aimbot", NoUI = false, Callback = function(s) Toggles.AimbotEnabled:SetValue(s); Aimbot.Enabled = s; if s then Ab_Start() else Ab_Stop() end end })

        FR:AddToggle("AutoShoot", { Text = "Auto Shoot", Default = false, Callback = function(v) AS.enabled = v; if v then AS_start() else AS_stop() end end })
        FR:AddSlider("ASRate", { Text = "Fire Rate", Default = 80, Min = 10, Max = 500, Rounding = 0, Callback = function(v) AS.fireRate = v / 1000 end })
        FR:AddSlider("ASDist", { Text = "Max Distance", Default = 1000, Min = 50, Max = 5000, Rounding = 0, Callback = function(v) AS.maxDist = v end })
        FR:AddSlider("ASAcc", { Text = "Accuracy (px)", Default = 40, Min = 5, Max = 150, Rounding = 0, Callback = function(v) AS.threshold = v end })
        FR:AddDropdown("ASPart", { Text = "Target Parts", Values = { "Head", "UpperTorso", "LowerTorso", "HumanoidRootPart", "RightUpperArm", "LeftUpperArm", "RightUpperLeg", "LeftUpperLeg" }, Default = 1, Multi = true, Callback = function(val) AS.TargetParts = {}; for pn, sel in pairs(val) do if sel then AS.TargetParts[#AS.TargetParts + 1] = pn end end; if #AS.TargetParts == 0 then AS.TargetParts = { "Head" } end end })
        FR:AddDivider()
        FR:AddLabel("Anti Hit")
        FR:AddToggle("AntiHitEn", { Text = "Anti Hit", Default = false, Callback = function(v) AntiHit.Enabled = v end })
        FR:AddDropdown("AntiHitItems", { Text = "Blocked Items", Values = { "Riot Shield" }, Default = 1, Multi = true, Callback = function(val) AntiHit.Blocked = {}; for n, s in pairs(val) do if s then AntiHit.Blocked[n] = true end end end })
        FR:AddDivider()
        local asKB = FR:AddLabel("Toggle Keybind"); asKB:AddKeyPicker("ASKeybind", { Default = "None", Mode = "Toggle", Text = "Auto Shoot", NoUI = false, Callback = function(s) Toggles.AutoShoot:SetValue(s); if s then AS_start() else AS_stop() end end })

        FU:AddButton({ Text = "Unlock All Cosmetics", Func = function() doUnlock() end })

        FAG:AddToggle("AGEn", { Text = "Anti Gadgets", Default = false, Callback = function(v) AG.Enabled = v; if v then AG_start() else AG_stop() end end })
        FAG:AddDropdown("AGItems", { Text = "Blocked Gadgets", Values = { "Smoke Grenade", "Flashbang", "Molotov" }, Default = 1, Multi = true, Callback = function(val)
            AG.BlockedSet = {}; for name, sel in pairs(val) do if sel then AG.BlockedSet[name] = true end end
            if AG.Enabled then
                for _, d in ipairs(workspace:GetDescendants()) do chkAny(d) end
                for _, d in ipairs(PGui:GetDescendants()) do chkAny(d) end
                for _, d in ipairs(Lighting:GetDescendants()) do chkAny(d) end
            end
        end })

        
        FMM:AddToggle("MMEnabled", { Text = "Auto Queue", Default = false, Callback = function(v)
            Matchmaking.Enabled = v
            if v then MM_JoinQueue() end
        end })
        FMM:AddDropdown("MMQueue", {
            Text = "Queue Mode",
            Values = { "1v1", "2v2", "3v3", "4v4", "5v5", "1v1_ranked", "2v2_ranked", "3v3_ranked", "4v4_ranked", "5v5_ranked" },
            Default = "2v2",
            Multi = false,
            Callback = function(v) Matchmaking.Selected = v end
        })
        
    end

    local function buildRageBot()
        local RBL = Tabs.RageBot:AddLeftGroupbox("RageBot")
        local RBR = Tabs.RageBot:AddRightGroupbox("Settings")
        local RBI = Tabs.RageBot:AddRightGroupbox("Info")

        RBI:AddLabel("Live Status")
        RB_StatusLabel = RBI:AddLabel("Status: IDLE")
        RBI:AddDivider()
        RBI:AddLabel("1. Enable RageBot")
        RBI:AddLabel("2. Instantly TPs above target")
        RBI:AddLabel("3. Auto fires using Silent Aim")
        RBI:AddLabel("4. Locks onto one player")
        RBI:AddLabel("Height 0 = goes behind target")

        RBL:AddToggle("RageBotEnabled", { Text = "Enable RageBot", Default = false, Callback = function(v)
            RageBot.Enabled = v
            if v then
                RageBot.lockedTarget = nil; RB_Start()
                Library:Notify({ Title = "RageBot", Description = "Active!", Time = 3 })
            else
                RB_Stop()
                Library:Notify({ Title = "RageBot", Description = "Disabled.", Time = 3 })
            end
        end })
        RBL:AddDivider()
        RBL:AddToggle("RBTeamCheck", { Text = "Team Check", Default = true, Callback = function(v) RageBot.TeamCheck = v end })
        RBL:AddToggle("RBVisCheck", { Text = "Visible Check", Default = false, Callback = function(v) RageBot.VisibleCheck = v end })
        RBL:AddDivider()
        RBL:AddSlider("RBFlyHeight", {
            Text = "Height Above Target", Default = 30, Min = 0, Max = 20000, Rounding = 0,
            Tooltip = "0 = go 4 studs behind target. Higher = further above.",
            Callback = function(v) RageBot.FlyHeight = v end
        })
        RBL:AddDivider()
        local rbKB = RBL:AddLabel("Toggle Keybind")
        rbKB:AddKeyPicker("RBKeybind", { Default = "None", Mode = "Toggle", Text = "RageBot", NoUI = false, Callback = function(s)
            Toggles.RageBotEnabled:SetValue(s); RageBot.Enabled = s
            if s then RageBot.lockedTarget = nil; RB_Start() else RB_Stop() end
        end })
        RBL:AddDivider()
        RBL:AddButton({ Text = "Force Stop", Func = function()
            Toggles.RageBotEnabled:SetValue(false); RageBot.Enabled = false; RB_Stop()
            Library:Notify({ Title = "RageBot", Description = "Force stopped.", Time = 3 })
        end })
        RBL:AddButton({ Text = "Reset Target Lock", Func = function()
            RageBot.lockedTarget = nil
            Library:Notify({ Title = "RageBot", Description = "Target lock reset.", Time = 2 })
        end })

        RBR:AddSlider("RBSAFov", { Text = "FOV Radius (px)", Default = 120, Min = 20, Max = 1000, Rounding = 0, Callback = function(v) RageBot.FOVRadius = v end })
        RBR:AddDivider()
        RBR:AddSlider("RBSAFireRate", {
            Text = "Fire Rate", Default = 8, Min = 1, Max = 200, Rounding = 0,
            Tooltip = "Lower = FASTER. Higher = SLOWER.",
            Callback = function(v) RageBot.FireRate = v / 100 end
        })
        RBR:AddDivider()
        local rbFovCol = RBR:AddLabel("FOV Circle Color")
        rbFovCol:AddColorPicker("RBFovCol", { Default = Color3.fromRGB(255, 100, 100), Title = "RageBot FOV", Callback = function(v) RB_FOVCircle.Color = v end })
    end

    local function buildESP()
        LeftGroupBox:AddToggle("ESPEnabled", { Text = "Enable ESP", Default = false, Callback = function(v) ESPS.Enabled = v end })
        LeftGroupBox:AddDivider()
        LeftGroupBox:AddToggle("ESPBox", { Text = "Box ESP", Default = false, Callback = function(v) ESPS.Box = v end })
        LeftGroupBox:AddToggle("ESPSkel", { Text = "Skeleton", Default = false, Callback = function(v) ESPS.Skeleton = v end })
        LeftGroupBox:AddToggle("ESPHBar", { Text = "Health Bar", Default = false, Callback = function(v) ESPS.HealthBar = v end })
        LeftGroupBox:AddToggle("ESPNames", { Text = "Names", Default = false, Callback = function(v) ESPS.Names = v end })
        LeftGroupBox:AddToggle("ESPDist", { Text = "Distance", Default = false, Callback = function(v) ESPS.Distance = v end })
        LeftGroupBox:AddToggle("ESPSnap", { Text = "Snap Lines", Default = false, Callback = function(v) ESPS.SnapLines = v end })
        LeftGroupBox:AddDivider()
        LeftGroupBox:AddToggle("ESPTeam", { Text = "Team Check", Default = false, Callback = function(v) ESPS.TeamCheck = v end })
        LeftGroupBox:AddDivider()
        LeftGroupBox:AddLabel("Trap ESP")
        LeftGroupBox:AddToggle("TripESP", { Text = "Subspace Tripmine", Default = false, Callback = function(v) TrapESP.SubspaceTripmine = v; if v then startTrip() else stopTrip() end end })
        local tcL = LeftGroupBox:AddLabel("Tripmine Color")
        tcL:AddColorPicker("TripColor", { Default = Color3.fromRGB(170, 0, 255), Title = "Tripmine Color", Callback = function(v)
            TrapESP.Color = v
            for _, o in ipairs(tripObjs) do
                if o.hl then o.hl.Color3 = v; o.hl.SurfaceColor3 = v end
                if o.lbl then o.lbl.TextColor3 = v end
            end
        end })
        LeftGroupBox:AddDivider()
        LeftGroupBox:AddLabel("Hotbar ESP")
        LeftGroupBox:AddToggle("HotbarESP", { Text = "Hotbar ESP", Default = false, Callback = function(v) HotbarESP.Enabled = v; if v then startHB() else stopHB() end end })
        LeftGroupBox:AddSlider("HBMaxDist", { Text = "Max Distance (studs)", Default = 100, Min = 0, Max = 500, Rounding = 0, Callback = function(v) HotbarESP.MaxDistance = v end })
        LeftGroupBox:AddDivider()
        local hbAC = LeftGroupBox:AddLabel("Equipped Gun Color")
        hbAC:AddColorPicker("HBActiveCol", { Default = Color3.fromRGB(255, 255, 255), Title = "Equipped Gun Color", Callback = function(v) HotbarESP.ActiveColor = v; refreshHBColors() end })
        local hbIC = LeftGroupBox:AddLabel("Other Guns Color")
        hbIC:AddColorPicker("HBInactiveCol", { Default = Color3.fromRGB(130, 130, 130), Title = "Other Guns Color", Callback = function(v) HotbarESP.InactiveColor = v; refreshHBColors() end })
        local hbSC = LeftGroupBox:AddLabel("Active Slot Border Color")
        hbSC:AddColorPicker("HBStrokeCol", { Default = Color3.fromRGB(70, 140, 255), Title = "Active Slot Border", Callback = function(v) HotbarESP.ActiveStroke = v; refreshHBColors() end })

        RightGroupBox:AddSlider("ESPMaxD", { Text = "Max Distance", Default = IsMobile and 400 or 1000, Min = 50, Max = 2000, Rounding = 0, Callback = function(v) ESPS.MaxDist = v end })
        RightGroupBox:AddSlider("ESPMinD", { Text = "Min Distance", Default = 0, Min = 0, Max = 30, Rounding = 0, Callback = function(v) ESPS.MinDist = v end })
        RightGroupBox:AddSlider("ESPFps", { Text = "Update Rate (FPS)", Default = 20, Min = 1, Max = 244, Rounding = 0, Callback = function(v) ESP_IVL = 1 / v end })
        RightGroupBox:AddDivider()
        RightGroupBox:AddDropdown("ESPSnapO", { Text = "Snap Line Origin", Values = { "Bottom", "Center", "Top" }, Default = "Bottom", Callback = function(v) ESPS.SnapOrigin = v end })
        RightGroupBox:AddDivider()
        local e1 = RightGroupBox:AddLabel("Box Color"); e1:AddColorPicker("ESPBoxC", { Default = Color3.fromRGB(255, 50, 50), Title = "Box", Callback = function(v) ESPS.BoxColor = v end })
        local e2 = RightGroupBox:AddLabel("Skeleton Color"); e2:AddColorPicker("ESPSkelC", { Default = Color3.fromRGB(255, 255, 255), Title = "Skeleton", Callback = function(v) ESPS.SkeletonColor = v end })
        RightGroupBox:AddDivider()
        local e3 = RightGroupBox:AddLabel("Health High"); e3:AddColorPicker("ESPHHi", { Default = Color3.fromRGB(0, 255, 100), Title = "HP High", Callback = function(v) ESPS.HealthHigh = v end })
        local e4 = RightGroupBox:AddLabel("Health Low"); e4:AddColorPicker("ESPHLo", { Default = Color3.fromRGB(255, 50, 50), Title = "HP Low", Callback = function(v) ESPS.HealthLow = v end })
        RightGroupBox:AddDivider()
        local e5 = RightGroupBox:AddLabel("Name Color"); e5:AddColorPicker("ESPNameC", { Default = Color3.fromRGB(255, 255, 255), Title = "Names", Callback = function(v) ESPS.NameColor = v end })
        local e6 = RightGroupBox:AddLabel("Distance Color"); e6:AddColorPicker("ESPDistC", { Default = Color3.fromRGB(255, 255, 100), Title = "Distance", Callback = function(v) ESPS.DistColor = v end })
        local e7 = RightGroupBox:AddLabel("Snap Line Color"); e7:AddColorPicker("ESPSnapC", { Default = Color3.fromRGB(255, 50, 50), Title = "Snap", Callback = function(v) ESPS.SnapColor = v end })
        RightGroupBox:AddDivider()
        RightGroupBox:AddLabel("Bullet Tracers")
        RightGroupBox:AddToggle("BTEnabled", { Text = "Bullet Tracers", Default = false, Callback = function(v)
            BT.Enabled = v; if v then BT_start() else BT_stop() end
        end })
        RightGroupBox:AddDropdown("BTStyle", { Text = "Tracer Style", Default = "Straight", Values = { "Straight", "Zigzag", "Lightning", "Rainbow" }, Callback = function(v) BT.Style = v end })
        RightGroupBox:AddSlider("BTFade", { Text = "Fade Time (s)", Default = 30, Min = 5, Max = 200, Rounding = 0, Callback = function(v) BT.FadeTime = v / 100 end })
        RightGroupBox:AddSlider("BTThick", { Text = "Thickness", Default = 5, Min = 1, Max = 20, Rounding = 0, Callback = function(v) BT.Thickness = v / 100 end })
        local btC = RightGroupBox:AddLabel("Tracer Color"); btC:AddColorPicker("BTColor", { Default = Color3.fromRGB(255, 60, 60), Title = "Bullet Tracer Color", Callback = function(v) BT.Color = v end })
    end

    local function buildPlayer()
        local PL = Tabs.Player:AddLeftGroupbox("Movement")
        local PR = Tabs.Player:AddRightGroupbox("Keybinds")

        PL:AddToggle("SpeedEn", { Text = "Speed Hack", Default = false, Callback = function(v) PS.SpeedEnabled = v; if v then rawSetWalkSpeed(hooks.walkspeed) else rawSetWalkSpeed(OrigWS) end end })
        PL:AddSlider("WalkSpd", { Text = "Walk Speed", Default = 16, Min = 16, Max = 500, Rounding = 0, Callback = function(v) hooks.walkspeed = v; if PS.SpeedEnabled then rawSetWalkSpeed(v) end end })
        PL:AddDivider()
        PL:AddToggle("SlideEn", { Text = "Slide Boost", Default = false, Callback = function(v) SlideBoost.Enabled = v end })
        PL:AddSlider("SlideMul", { Text = "Slide Multiplier", Default = 2, Min = 1, Max = 10, Rounding = 1, Callback = function(v) SlideBoost.Multiplier = v end })
        PL:AddDivider()
        PL:AddToggle("FlyEn", { Text = "Fly", Default = false, Callback = function(v) FlySettings.Enabled = v; if v then enableFly() else disableFly() end end })
        PL:AddSlider("FlySpd", { Text = "Fly Speed", Default = 50, Min = 10, Max = 500, Rounding = 0, Callback = function(v) FlySettings.Speed = v end })
        PL:AddDivider()
        PL:AddToggle("JumpEn", { Text = "Jump Power Hack", Default = false, Callback = function(v) PS.JumpEnabled = v; if v then rawSetJumpPower(hooks.jumppower) else rawSetJumpPower(OrigJP) end end })
        PL:AddSlider("JumpPow", { Text = "Jump Power", Default = 50, Min = 50, Max = 500, Rounding = 0, Callback = function(v) hooks.jumppower = v; if PS.JumpEnabled then rawSetJumpPower(v) end end })
        PL:AddDivider()
        PL:AddToggle("NoclipEn", { Text = "Noclip", Default = false, Callback = function(v) PS.NoclipEnabled = v; if not v then setCollision(true) end end })
        PL:AddToggle("InfJump", { Text = "Infinite Jump", Default = false, Callback = function(v) PS.InfiniteJump = v end })
        PL:AddDivider()
        PL:AddButton({ Text = "Reset All Player Settings", Func = function()
            Toggles.SpeedEn:SetValue(false); Toggles.JumpEn:SetValue(false)
            Toggles.NoclipEn:SetValue(false); Toggles.InfJump:SetValue(false)
            Toggles.FlyEn:SetValue(false); Toggles.SlideEn:SetValue(false)
            Options.WalkSpd:SetValue(16); Options.JumpPow:SetValue(50)
            Options.FlySpd:SetValue(50); Options.SlideMul:SetValue(2)
            hooks.walkspeed = 16; hooks.jumppower = 50
            SlideBoost.Enabled = false; SlideBoost.Multiplier = 2
            setCollision(true); FlySettings.Enabled = false; disableFly()
            Library:Notify({ Title = "Player", Description = "Reset to defaults", Time = 3 })
        end })

        local k1 = PR:AddLabel("Slide Boost"); k1:AddKeyPicker("SlideKB", { Default = "None", Mode = "Toggle", Text = "Slide Boost", NoUI = false, Callback = function(s) Toggles.SlideEn:SetValue(s); SlideBoost.Enabled = s end })
        PR:AddDivider()
        local k2 = PR:AddLabel("Speed Hack"); k2:AddKeyPicker("SpeedKB", { Default = "None", Mode = "Toggle", Text = "Speed", NoUI = false, Callback = function(s) Toggles.SpeedEn:SetValue(s) end })
        PR:AddDivider()
        local k3 = PR:AddLabel("Fly"); k3:AddKeyPicker("FlyKB", { Default = "None", Mode = "Toggle", Text = "Fly", NoUI = false, Callback = function(s) Toggles.FlyEn:SetValue(s); FlySettings.Enabled = s; if s then enableFly() else disableFly() end end })
        PR:AddDivider()
        local k4 = PR:AddLabel("Jump Power"); k4:AddKeyPicker("JumpKB", { Default = "None", Mode = "Toggle", Text = "Jump", NoUI = false, Callback = function(s) Toggles.JumpEn:SetValue(s) end })
        PR:AddDivider()
        local k5 = PR:AddLabel("Noclip"); k5:AddKeyPicker("NoclipKB", { Default = "None", Mode = "Toggle", Text = "Noclip", NoUI = false, Callback = function(s) Toggles.NoclipEn:SetValue(s); if not s then setCollision(true) end end })
        PR:AddDivider()
        local k6 = PR:AddLabel("Infinite Jump"); k6:AddKeyPicker("InfJumpKB", { Default = "None", Mode = "Toggle", Text = "Inf Jump", NoUI = false, Callback = function(s) Toggles.InfJump:SetValue(s) end })
    end

    local function buildWorld()
        local WF = Tabs.World:AddLeftGroupbox("Freecam")
        local WEL = Tabs.World:AddLeftGroupbox("World Effects")
        local WER = Tabs.World:AddRightGroupbox("Post Processing")

        WF:AddToggle("FCEn", { Text = "Enable Freecam", Default = false, Callback = function(v) FreeCam.Enabled = v; if v then FC_Enable() else FC_Disable() end end })
        WF:AddSlider("FCSpd", { Text = "Fly Speed", Default = 50, Min = 5, Max = 500, Rounding = 0, Callback = function(v) FreeCam.Speed = v end })
        local fcKB = WF:AddLabel("Toggle Keybind"); fcKB:AddKeyPicker("FCKB", { Default = "None", Mode = "Toggle", Text = "Freecam", NoUI = false, Callback = function(s) Toggles.FCEn:SetValue(s); if s then FC_Enable() else FC_Disable() end end })

        WEL:AddToggle("WESkyEn", { Text = "Custom Sky / Ambient", Default = false, Callback = function(v) WE.SkyEnabled = v; if v then applySkyClock() else removeSky() end end })
        local skyCol = WEL:AddLabel("Sky Tint"); skyCol:AddColorPicker("WESkyCol", { Default = Color3.fromRGB(30, 60, 120), Title = "Sky Tint", Callback = function(v)
            WE.SkyColor = v; WE.AmbientColor = Color3.new(v.R * 0.5, v.G * 0.5, v.B * 0.5)
            WE.OutdoorAmbient = Color3.new(math.clamp(v.R * 0.8, 0, 1), math.clamp(v.G * 0.8, 0, 1), math.clamp(v.B * 0.8, 0, 1))
            if WE.SkyEnabled then applySkyClock() end
        end })
        local ambCol = WEL:AddLabel("Ambient Color"); ambCol:AddColorPicker("WEAmbCol", { Default = Color3.fromRGB(70, 70, 70), Title = "Ambient", Callback = function(v) WE.AmbientColor = v; if WE.SkyEnabled then Lighting.Ambient = v end end })
        local outCol = WEL:AddLabel("Outdoor Ambient"); outCol:AddColorPicker("WEOutCol", { Default = Color3.fromRGB(100, 100, 140), Title = "Outdoor Ambient", Callback = function(v) WE.OutdoorAmbient = v; if WE.SkyEnabled then Lighting.OutdoorAmbient = v end end })
        WEL:AddDivider()
        WEL:AddToggle("WEBrightEn", { Text = "Custom Brightness", Default = false, Callback = function(v) WE.BrightnessEnabled = v; applyBrightness() end })
        WEL:AddSlider("WEBright", { Text = "Brightness Level", Default = 100, Min = 0, Max = 1000, Rounding = 0, Callback = function(v) WE.Brightness = v / 100; if WE.BrightnessEnabled then applyBrightness() end end })
        WEL:AddDivider()
        WEL:AddToggle("WEFogEn", { Text = "Custom Fog", Default = false, Callback = function(v) WE.FogEnabled = v; applyFog() end })
        local fogCol = WEL:AddLabel("Fog Color"); fogCol:AddColorPicker("WEFogCol", { Default = Color3.fromRGB(180, 200, 220), Title = "Fog Color", Callback = function(v) WE.FogColor = v; if WE.FogEnabled then applyFog() end end })
        WEL:AddSlider("WEFogS", { Text = "Fog Start", Default = 0, Min = 0, Max = 1000, Rounding = 0, Callback = function(v) WE.FogStart = v; if WE.FogEnabled then applyFog() end end })
        WEL:AddSlider("WEFogE", { Text = "Fog End", Default = 300, Min = 10, Max = 5000, Rounding = 0, Callback = function(v) WE.FogEnd = v; if WE.FogEnabled then applyFog() end end })
        WEL:AddDivider()
        WEL:AddToggle("WETimeEn", { Text = "Custom Time of Day", Default = false, Callback = function(v) WE.TimeEnabled = v; applyTime() end })
        WEL:AddSlider("WETime", { Text = "Hour", Default = 14, Min = 0, Max = 24, Rounding = 1, Callback = function(v) WE.TimeOfDay = v; if WE.TimeEnabled then applyTime() end end })
        WEL:AddDivider()
        WEL:AddToggle("WESnowEn", { Text = "Enable Snow", Default = false, Callback = function(v) if v then buildSnow() else clearSnow() end end })
        WEL:AddSlider("WESnowSpeed", { Text = "Fall Speed", Default = 10, Min = 1, Max = 50, Rounding = 0, Callback = function(v) WE.SnowSpeed = v / 10; if snowEmitter then snowEmitter.Speed = NumberRange.new(3 * WE.SnowSpeed, 7 * WE.SnowSpeed) end end })
        WEL:AddSlider("WESnowDensity", { Text = "Density", Default = 200, Min = 10, Max = 800, Rounding = 0, Callback = function(v) WE.SnowDensity = v; if snowEmitter then snowEmitter.Rate = v end end })
        WEL:AddSlider("WESnowSize", { Text = "Flake Size", Default = 30, Min = 5, Max = 100, Rounding = 0, Callback = function(v) WE.SnowSize = v / 100; if snowEmitter then snowEmitter.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, WE.SnowSize), NumberSequenceKeypoint.new(1, WE.SnowSize * 0.5) }) end end })
        local snwCol = WEL:AddLabel("Snow Color"); snwCol:AddColorPicker("WESnowCol", { Default = Color3.fromRGB(255, 255, 255), Title = "Snow Color", Callback = function(v) WE.SnowColor = v; if snowEmitter then snowEmitter.Color = ColorSequence.new(v) end end })
        WEL:AddDivider()
        WEL:AddToggle("WERainEn", { Text = "Enable Rain", Default = false, Callback = function(v) if v then buildRain() else clearRain() end end })
        WEL:AddSlider("WERainSpeed", { Text = "Rain Speed", Default = 30, Min = 5, Max = 100, Rounding = 0, Callback = function(v) WE.RainSpeed = v / 10; if rainEmitter then rainEmitter.Speed = NumberRange.new(28 * WE.RainSpeed, 40 * WE.RainSpeed) end end })
        WEL:AddSlider("WERainDensity", { Text = "Density", Default = 300, Min = 20, Max = 1000, Rounding = 0, Callback = function(v) WE.RainDensity = v; if rainEmitter then rainEmitter.Rate = v end end })
        WEL:AddDivider()
        WEL:AddButton({ Text = "Night", Func = function()
            Options.WETime:SetValue(0); Options.WEBright:SetValue(20)
            Options.WEFogS:SetValue(0); Options.WEFogE:SetValue(200)
            Toggles.WETimeEn:SetValue(true); Toggles.WEBrightEn:SetValue(true); Toggles.WEFogEn:SetValue(true)
        end })
        WEL:AddButton({ Text = "Sunset", Func = function()
            Options.WETime:SetValue(18); Options.WEBright:SetValue(150)
            Toggles.WETimeEn:SetValue(true); Toggles.WEBrightEn:SetValue(true)
        end })
        WEL:AddButton({ Text = "Blizzard", Func = function()
            Options.WESnowSpeed:SetValue(40); Options.WESnowDensity:SetValue(700)
            Options.WEBright:SetValue(180); Options.WEFogS:SetValue(0); Options.WEFogE:SetValue(150)
            Toggles.WESnowEn:SetValue(true); Toggles.WEBrightEn:SetValue(true); Toggles.WEFogEn:SetValue(true)
        end })
        WEL:AddButton({ Text = "Thunderstorm", Func = function()
            Options.WERainSpeed:SetValue(80); Options.WERainDensity:SetValue(800)
            Options.WEBright:SetValue(30); Options.WEFogS:SetValue(0); Options.WEFogE:SetValue(300)
            Toggles.WERainEn:SetValue(true); Toggles.WEBrightEn:SetValue(true); Toggles.WEFogEn:SetValue(true)
        end })
        WEL:AddButton({ Text = "Reset All", Func = function()
            Toggles.WESkyEn:SetValue(false); Toggles.WEBrightEn:SetValue(false)
            Toggles.WEFogEn:SetValue(false); Toggles.WETimeEn:SetValue(false)
            Toggles.WESnowEn:SetValue(false); Toggles.WERainEn:SetValue(false)
            Toggles.WEBloomEn:SetValue(false); Toggles.WEBlurEn:SetValue(false)
            Toggles.WECCEn:SetValue(false); Toggles.WEDOFEn:SetValue(false); Toggles.WESunEn:SetValue(false)
        end })

        WER:AddToggle("WEBloomEn", { Text = "Enable Bloom", Default = false, Callback = function(v) WE.BloomEnabled = v; applyBloom() end })
        WER:AddSlider("WEBloomInt", { Text = "Intensity", Default = 50, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.BloomIntensity = v / 100; if WE.BloomEnabled then applyBloom() end end })
        WER:AddSlider("WEBloomSz", { Text = "Size", Default = 24, Min = 1, Max = 56, Rounding = 0, Callback = function(v) WE.BloomSize = v; if WE.BloomEnabled then applyBloom() end end })
        WER:AddSlider("WEBloomTh", { Text = "Threshold", Default = 95, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.BloomThreshold = v / 100; if WE.BloomEnabled then applyBloom() end end })
        WER:AddDivider()
        WER:AddToggle("WEBlurEn", { Text = "Enable Blur", Default = false, Callback = function(v) WE.BlurEnabled = v; applyBlur() end })
        WER:AddSlider("WEBlurSz", { Text = "Blur Size", Default = 8, Min = 0, Max = 56, Rounding = 0, Callback = function(v) WE.BlurSize = v; if WE.BlurEnabled then applyBlur() end end })
        WER:AddDivider()
        WER:AddToggle("WECCEn", { Text = "Enable Color Correction", Default = false, Callback = function(v) WE.CCEnabled = v; applyCC() end })
        WER:AddSlider("WECCBri", { Text = "Brightness", Default = 0, Min = -100, Max = 100, Rounding = 0, Callback = function(v) WE.CCBrightness = v / 100; if WE.CCEnabled then applyCC() end end })
        WER:AddSlider("WECCCon", { Text = "Contrast", Default = 0, Min = -100, Max = 100, Rounding = 0, Callback = function(v) WE.CCContrast = v / 100; if WE.CCEnabled then applyCC() end end })
        WER:AddSlider("WECCSat", { Text = "Saturation", Default = 0, Min = -100, Max = 100, Rounding = 0, Callback = function(v) WE.CCSaturation = v / 100; if WE.CCEnabled then applyCC() end end })
        local ccTint = WER:AddLabel("Color Tint"); ccTint:AddColorPicker("WECCTint", { Default = Color3.fromRGB(255, 255, 255), Title = "Color Tint", Callback = function(v) WE.CCTintColor = v; if WE.CCEnabled then applyCC() end end })
        WER:AddDivider()
        WER:AddToggle("WEDOFEn", { Text = "Enable Depth of Field", Default = false, Callback = function(v) WE.DOFEnabled = v; applyDOF() end })
        WER:AddSlider("WEDOFFar", { Text = "Far Intensity", Default = 100, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.DOFFarIntensity = v / 100; if WE.DOFEnabled then applyDOF() end end })
        WER:AddSlider("WEDOFFocus", { Text = "Focus Distance", Default = 50, Min = 0, Max = 500, Rounding = 0, Callback = function(v) WE.DOFFocusDistance = v; if WE.DOFEnabled then applyDOF() end end })
        WER:AddSlider("WEDOFRadius", { Text = "Focus Radius", Default = 10, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.DOFInFocusRadius = v; if WE.DOFEnabled then applyDOF() end end })
        WER:AddSlider("WEDOFNear", { Text = "Near Intensity", Default = 100, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.DOFNearIntensity = v / 100; if WE.DOFEnabled then applyDOF() end end })
        WER:AddDivider()
        WER:AddToggle("WESunEn", { Text = "Enable Sun Rays", Default = false, Callback = function(v) WE.SunRaysEnabled = v; applySunRays() end })
        WER:AddSlider("WESunInt", { Text = "Intensity", Default = 10, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.SunRaysIntensity = v / 100; if WE.SunRaysEnabled then applySunRays() end end })
        WER:AddSlider("WESunSpread", { Text = "Spread", Default = 50, Min = 0, Max = 100, Rounding = 0, Callback = function(v) WE.SunRaysSpread = v / 100; if WE.SunRaysEnabled then applySunRays() end end })
    end

    local function buildCrosshair()
        local CL = Tabs.Crosshair:AddLeftGroupbox("Crosshair Settings")
        local CR = Tabs.Crosshair:AddRightGroupbox("Style & Animation")

        
        CL:AddToggle("BrandingToggle", { Text = "Discord Server Branding", Default = true, Callback = function(v)
            CH.BrandingVisible = v
            brandHolder.Visible = v
        end })
        CL:AddDivider()
        CR:AddDropdown("CHEffectMode", { Text = "Color Effect", Values = { "Default", "Rainbow", "Pulse Rainbow", "Neon Flicker", "Fire", "Ocean Wave", "Synthwave", "Gold Shimmer", "Blood Moon", "Matrix" }, Default = "Default", Callback = function(v) CHEffect.Mode = v; CHEffect.t = 0 end })
        CR:AddDivider()
        local cc = CL:AddLabel("Base Color"); cc:AddColorPicker("CHCol", { Default = Color3.fromRGB(255, 255, 255), Title = "Crosshair Color", Callback = function(v) CH.Color = v; CHEffect.BaseColor = v; if CHEffect.Mode == "Default" then syncColor(v) end end })
        CL:AddDivider()
        CL:AddSlider("CHGap", { Text = "Gap", Default = 10, Min = 0, Max = 40, Rounding = 0, Callback = function(v) CH.baseGap = v end })
        CL:AddSlider("CHTh", { Text = "Thickness", Default = 2, Min = 1, Max = 8, Rounding = 0, Callback = function(v) CH.Thick = v; applyStyle() end })
        CL:AddSlider("CHLen", { Text = "Arm Length", Default = 10, Min = 5, Max = 40, Rounding = 0, Callback = function(v) CH.Len = v; applyStyle() end })
        CL:AddSlider("CHLen2", { Text = "Shape Size", Default = 20, Min = 8, Max = 60, Rounding = 0, Callback = function(v) CH.Len2 = v; applyStyle() end })
        CL:AddSlider("CHDot", { Text = "Dot Size", Default = 4, Min = 0, Max = 20, Rounding = 0, Callback = function(v) CH.Dot = v end })
        CR:AddDropdown("CHStyle", { Text = "Style", Values = { "Cross", "Square", "Star", "T-Shape", "Circle", "Arrow", "X", "Dot Only", "Tactical" }, Default = "Cross", Callback = function(v) CH.Style = v; applyStyle() end })
        CR:AddDivider()
        CR:AddDropdown("CHAnim", { Text = "Animations", Values = { "Spin", "Pulse" }, Default = 1, Multi = true, Callback = function(v) CH.Anim = {}; for k, sel in pairs(v) do if sel then CH.Anim[#CH.Anim + 1] = k end end end })
        CR:AddDivider()
        CR:AddSlider("CHSpinI", { Text = "Spin Intensity", Default = 1, Min = 0, Max = 5, Rounding = 1, Callback = function(v) CH.SpinI = v end })
        CR:AddSlider("CHPulseI", { Text = "Pulse Intensity", Default = 1, Min = 0, Max = 5, Rounding = 1, Callback = function(v) CH.PulseI = v end })
    end

    local function buildSpoof()
        local SL = Tabs.Spoof:AddLeftGroupbox("Device Spoofer")
        local SR = Tabs.Spoof:AddRightGroupbox("Info")

        SR:AddLabel("Spoofs your control type")
        SR:AddLabel("to the server at the top / scoreboard.")
        SR:AddDivider()
        SR:AddLabel("Computer = Mouse & Keyboard")
        SR:AddLabel("Mobile = Touch Controls")
        SR:AddLabel("Console = Gamepad")
        SR:AddLabel("VR = VR Controls")

        SL:AddToggle("DeviceSpoofEn", { Text = "Enable Device Spoofer", Default = false, Callback = function(v) DeviceSpoof.Enabled = v; if v then applySpoofs() end end })
        SL:AddDivider()
        SL:AddDropdown("DeviceSpoofType", { Text = "Spoof As", Values = { "Computer", "Mobile", "Console", "VR" }, Default = "Computer", Multi = false, Callback = function(v) DeviceSpoof.Selected = v; if DeviceSpoof.Enabled then applySpoofs() end end })
    end

    local function buildUISettings()
        local MG = Tabs["UI Settings"]:AddLeftGroupbox("Menu")
        MG:AddToggle("KBMenuOpen", { Default = Library.KeybindFrame and Library.KeybindFrame.Visible or false, Text = "Open Keybind Menu", Callback = function(v) if Library.KeybindFrame then Library.KeybindFrame.Visible = v end end })
        MG:AddDivider()
        MG:AddToggle("CustomCursor", { Text = "Custom Cursor", Default = true, Callback = function(v) Library.ShowCustomCursor = v end })
        MG:AddDivider()
        MG:AddDropdown("NotifSide", { Values = { "Left", "Right" }, Default = "Right", Text = "Notification Side", Callback = function(v) Library:SetNotifySide(v) end })
        MG:AddDivider()
        MG:AddDropdown("DPI", { Values = { "50%", "75%", "100%", "125%", "150%", "175%", "200%" }, Default = "100%", Text = "DPI Scale", Callback = function(v) Library:SetDPIScale(tonumber(v:gsub("%%", ""))) end })
        MG:AddDivider()
        local mk = MG:AddLabel("Menu Toggle Keybind"); mk:AddKeyPicker("MenuKB", { Default = "RightShift", NoUI = true, Text = "Menu keybind" })
        MG:AddDivider()
        MG:AddButton("Unload", function() Library:Unload() end)
    end

    buildFighting()
    buildRageBot()
    buildESP()
    buildPlayer()
    buildWorld()
    buildCrosshair()
    buildSpoof()
    buildUISettings()

    Library.ToggleKeybind = Options.MenuKB
    ThemeManager:SetLibrary(Library)
    SaveManager:SetLibrary(Library)
    SaveManager:IgnoreThemeSettings()
    SaveManager:SetIgnoreIndexes({ "MenuKB", "SpeedKB", "JumpKB", "NoclipKB", "InfJumpKB", "ASKeybind", "SAKeybind", "FCKB", "FlyKB", "AbKeybind", "SlideKB", "RBKeybind" })
    ThemeManager:SetFolder("Crystalized")
    SaveManager:SetFolder("Crystalized/configs")
    SaveManager:BuildConfigSection(Tabs["UI Settings"])
    ThemeManager:ApplyToTab(Tabs["UI Settings"])
    SaveManager:LoadAutoloadConfig()

    Library:Notify({ Title = "Crystalized", Description = "Loaded! RightShift to toggle menu.", Time = 6 })
end
