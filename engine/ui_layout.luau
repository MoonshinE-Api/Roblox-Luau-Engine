-- Headless layout solver. Container autosizing is solved to a bounded fixed
-- point. Text shaping and flex-item grow/shrink rules require separate engines.
return function(R)
    local V2=R.datatypes.Vector2
    local rawRect=R.uiRect
    local revision=0
    local changed=R.changed
    function R.changed(object,key) revision+=1;changed(object,key) end
    local caches=setmetatable({}, {__mode='k'})
    local custom=setmetatable({}, {__mode='k'})
    local function weak() return setmetatable({}, {__mode='k'}) end
    local function props(object) return R.instances[object].props end
    local function modifier(object,class)
        for _,child in object:GetChildren() do if child:IsA(class) then return child end end
    end
    local function automatic(mode,axis)
        return mode==R.Enum.AutomaticSize.XY or mode==(if axis==1 then R.Enum.AutomaticSize.X else R.Enum.AutomaticSize.Y)
    end
    local function pixels(value,length,scale) return value.Scale*length+value.Offset*scale end
    local function padding(object,size,scale)
        local p=modifier(object,'UIPadding')
        if not p then return V2.zero,V2.zero,size end
        local start=V2.new(pixels(p.PaddingLeft,size.X,scale),pixels(p.PaddingTop,size.Y,scale))
        local finish=V2.new(pixels(p.PaddingRight,size.X,scale),pixels(p.PaddingBottom,size.Y,scale))
        return start,finish,(size-start-finish):Max(V2.zero)
    end
    local function align(horizontal)
        if horizontal==R.Enum.HorizontalAlignment.Center or horizontal==R.Enum.VerticalAlignment.Center then return 0.5 end
        if horizontal==R.Enum.HorizontalAlignment.Right or horizontal==R.Enum.VerticalAlignment.Bottom then return 1 end
        return 0
    end
    local function rootOf(object)
        if object:IsA('UIGridStyleLayout') then object=object.Parent end
        if not object or (not object:IsA('GuiObject') and not object:IsA('ScreenGui')) then return nil end
        while object.Parent and (object.Parent:IsA('GuiObject') or object.Parent:IsA('ScreenGui')) do object=object.Parent end
        return object
    end
    local function children(object,layout)
        local result={};local ordinal={}
        for i,child in object:GetChildren() do
            if child:IsA('GuiObject') then table.insert(result,child);ordinal[child]=i end
        end
        if layout then
            table.sort(result,function(a,b)
                if layout.SortOrder==R.Enum.SortOrder.Name and a.Name~=b.Name then return a.Name<b.Name end
                if layout.SortOrder==R.Enum.SortOrder.LayoutOrder and a.LayoutOrder~=b.LayoutOrder then return a.LayoutOrder<b.LayoutOrder end
                if layout.SortOrder==R.Enum.SortOrder.Custom and custom[layout] then
                    return custom[layout](a,b)
                end
                return ordinal[a]<ordinal[b]
            end)
        end
        return result
    end
    local function boundedSize(object,size,scale)
        local limit=modifier(object,'UISizeConstraint')
        if limit then size=size:Max(limit.MinSize*scale):Min(limit.MaxSize*scale) end
        local aspect=modifier(object,'UIAspectRatioConstraint')
        if aspect then
            assert(aspect.AspectRatio>0,'AspectRatio must be positive')
            local maximum=size
            if aspect.DominantAxis==R.Enum.DominantAxis.Width then size=V2.new(size.X,size.X/aspect.AspectRatio)
            else size=V2.new(size.Y*aspect.AspectRatio,size.Y) end
            if aspect.AspectType==R.Enum.AspectType.FitWithinMaxSize then
                size*=math.min(1,if size.X==0 then 1 else maximum.X/size.X,if size.Y==0 then 1 else maximum.Y/size.Y)
            end
        end
        return size:Max(V2.zero)
    end
    local function solve(root)
        local existing=caches[root]
        if existing and existing.revision==revision then return existing end
        local initialRevision=revision
        local rootPosition,rootSize,rootScale,rootRotation=rawRect(root)
        local seeds={}
        local final
        for iteration=1,96 do
            local nodes,layouts,canvases=weak(),weak(),weak()
            local nextSeeds={};local unsettled=false
            local measure
            measure=function(object,parentSize,parentScale,forcedSize,isRoot)
                local p=props(object)
                local scale=parentScale
                for _,child in object:GetChildren() do if child:IsA('UIScale') then scale*=child.Scale end end
                local basis=parentSize
                if p.SizeConstraint==R.Enum.SizeConstraint.RelativeXX then basis=V2.new(parentSize.X,parentSize.X)
                elseif p.SizeConstraint==R.Enum.SizeConstraint.RelativeYY then basis=V2.new(parentSize.Y,parentSize.Y) end
                local minimum=if isRoot then rootSize else
                    (forcedSize or V2.new(pixels(p.Size.X,basis.X,parentScale),pixels(p.Size.Y,basis.Y,parentScale))):Max(V2.zero)
                minimum*=if parentScale==0 then 0 else scale/parentScale
                local size=minimum
                if isRoot then size=rootSize;scale=rootScale
                elseif p.AutomaticSize~=R.Enum.AutomaticSize.None then
                    assert(not p.Text or p.Text=='','Intrinsic text AutomaticSize requires text shaping')
                    local seed=seeds[object] or minimum
                    size=V2.new(if automatic(p.AutomaticSize,1) then math.max(minimum.X,seed.X) else minimum.X,
                        if automatic(p.AutomaticSize,2) then math.max(minimum.Y,seed.Y) else minimum.Y)
                end
                if not isRoot then size=boundedSize(object,size,scale) end
                local start,finish,available=padding(object,size,scale)
                local node={size=size,scale=scale,relative=V2.zero,rotation=p.Rotation or 0}
                nodes[object]=node
                local layout=modifier(object,'UIGridStyleLayout')
                assert(not layout or layout:IsA('UIListLayout') or layout:IsA('UIGridLayout'),'This UI layout is not implemented')
                local list=children(object,layout)
                local live={};for _,child in list do if child.Visible then table.insert(live,child) end end
                local content=V2.zero
                local gridData
                if layout and layout:IsA('UIGridLayout') then
                    local cell=V2.new(pixels(layout.CellSize.X,available.X,scale),pixels(layout.CellSize.Y,available.Y,scale)):Max(V2.zero)
                    local gap=V2.new(pixels(layout.CellPadding.X,available.X,scale),pixels(layout.CellPadding.Y,available.Y,scale)):Max(V2.zero)
                    local horizontal=layout.FillDirection==R.Enum.FillDirection.Horizontal
                    local length=if horizontal then available.X else available.Y
                    local step=if horizontal then cell.X+gap.X else cell.Y+gap.Y
                    local pad=if horizontal then gap.X else gap.Y
                    local capacity=if step>0 then math.max(1,math.floor((length+pad)/step+1e-9)) else math.max(1,#live)
                    if layout.FillDirectionMaxCells>0 then capacity=math.min(capacity,math.max(1,math.floor(layout.FillDirectionMaxCells))) end
                    local spans={}
                    for _,child in live do
                        local limit=modifier(child,'UISizeConstraint')
                        local lower=if limit then limit.MinSize*scale else cell
                        local span=V2.new(if cell.X+gap.X>0 then math.max(1,math.ceil((lower.X+gap.X)/(cell.X+gap.X)-1e-9)) else 1,
                            if cell.Y+gap.Y>0 then math.max(1,math.ceil((lower.Y+gap.Y)/(cell.Y+gap.Y)-1e-9)) else 1)
                        spans[child]=span;capacity=math.max(capacity,if horizontal then span.X else span.Y)
                    end
                    local occupied={};local counts=V2.zero
                    local placements={}
                    for _,child in live do
                        local span=spans[child];local row,column=0,0
                        local spanA,spanB=if horizontal then span.X else span.Y,if horizontal then span.Y else span.X
                        while true do
                            local fits=column+spanA<=capacity
                            if fits then
                                for b=row,row+spanB-1 do
                                    for a=column,column+spanA-1 do if occupied[b*capacity+a] then fits=false;break end end
                                    if not fits then break end
                                end
                            end
                            if fits then break end
                            column+=1;if column>=capacity then column=0;row+=1 end
                        end
                        for b=row,row+spanB-1 do for a=column,column+spanA-1 do occupied[b*capacity+a]=true end end
                        local xy=if horizontal then V2.new(column,row) else V2.new(row,column)
                        placements[child]=xy
                        counts=counts:Max(xy+span)
                    end
                    content=V2.new(math.max(0,counts.X*cell.X+math.max(0,counts.X-1)*gap.X),
                        math.max(0,counts.Y*cell.Y+math.max(0,counts.Y-1)*gap.Y))
                    local origin=V2.new((available.X-content.X)*align(layout.HorizontalAlignment),(available.Y-content.Y)*align(layout.VerticalAlignment))
                    for _,child in list do
                        local span=spans[child] or V2.one
                        local forced=V2.new(span.X*cell.X+(span.X-1)*gap.X,span.Y*cell.Y+(span.Y-1)*gap.Y)
                        measure(child,available,scale,forced,false)
                        if child.Visible then
                            local xy=placements[child];local relative=xy*(cell+gap)
                            local corner=layout.StartCorner
                            if corner==R.Enum.StartCorner.TopRight or corner==R.Enum.StartCorner.BottomRight then relative=V2.new(content.X-relative.X-forced.X,relative.Y) end
                            if corner==R.Enum.StartCorner.BottomLeft or corner==R.Enum.StartCorner.BottomRight then relative=V2.new(relative.X,content.Y-relative.Y-forced.Y) end
                            nodes[child].relative=start+origin+relative
                        else nodes[child].relative=start end
                    end
                    gridData={content=content,cellSize=cell,cellCount=counts}
                else
                    for _,child in list do measure(child,available,scale,nil,false) end
                    if layout then
                        assert(layout.HorizontalFlex==R.Enum.UIFlexAlignment.None and layout.VerticalFlex==R.Enum.UIFlexAlignment.None,
                            'Flex grow/shrink layout is not implemented')
                        assert(layout.ItemLineAlignment==R.Enum.ItemLineAlignment.Automatic,'Flex item-line alignment is not implemented')
                        local horizontal=layout.FillDirection==R.Enum.FillDirection.Horizontal
                        local gap=pixels(layout.Padding,if horizontal then available.X else available.Y,scale)
                        local lines={{items={},main=0,cross=0}}
                        local limit=if horizontal then available.X else available.Y
                        for _,child in live do
                            assert(not modifier(child,'UIFlexItem'),'UIFlexItem layout is not implemented')
                            local s=nodes[child].size
                            local main,cross=if horizontal then s.X else s.Y,if horizontal then s.Y else s.X
                            local line=lines[#lines]
                            if layout.Wraps and #line.items>0 and line.main+gap+main>limit+1e-8 then
                                line={items={},main=0,cross=0};table.insert(lines,line)
                            end
                            line.main+=if #line.items>0 then gap+main else main
                            line.cross=math.max(line.cross,cross);table.insert(line.items,child)
                        end
                        local totalMain,totalCross=0,0
                        for i,line in lines do totalMain=math.max(totalMain,line.main);totalCross+=line.cross+(if i>1 then gap else 0) end
                        content=if horizontal then V2.new(totalMain,totalCross) else V2.new(totalCross,totalMain)
                        local crossOffset=((if horizontal then available.Y else available.X)-totalCross)
                            *align(if horizontal then layout.VerticalAlignment else layout.HorizontalAlignment)
                        for _,line in lines do
                            local cursor=((if horizontal then available.X else available.Y)-line.main)
                                *align(if horizontal then layout.HorizontalAlignment else layout.VerticalAlignment)
                            for _,child in line.items do
                                local s=nodes[child].size
                                local cross=(line.cross-(if horizontal then s.Y else s.X))
                                    *align(if horizontal then layout.VerticalAlignment else layout.HorizontalAlignment)
                                nodes[child].relative=start+(if horizontal then V2.new(cursor,crossOffset+cross) else V2.new(crossOffset+cross,cursor))
                                nodes[child].rotation=0
                                cursor+=(if horizontal then s.X else s.Y)+gap
                            end
                            crossOffset+=line.cross+gap
                        end
                        for _,child in list do if not child.Visible then nodes[child].relative=start end end
                        gridData={content=content}
                    else
                        for _,child in list do
                            local cp=props(child);local s=nodes[child].size
                            local offset=V2.new(pixels(cp.Position.X,available.X,scale),pixels(cp.Position.Y,available.Y,scale))-cp.AnchorPoint*s
                            nodes[child].relative=start+offset
                            if child.Visible then content=content:Max(offset+s) end
                        end
                    end
                end
                if layout then layouts[layout]=gridData end
                local demand=content+start+finish
                if not isRoot and p.AutomaticSize~=R.Enum.AutomaticSize.None then
                    local nextSize=boundedSize(object,V2.new(if automatic(p.AutomaticSize,1) then math.max(minimum.X,demand.X) else minimum.X,
                        if automatic(p.AutomaticSize,2) then math.max(minimum.Y,demand.Y) else minimum.Y),scale)
                    nextSeeds[object]=nextSize
                    if (nextSize-size).Magnitude>0.00001 then unsettled=true end
                end
                if object:IsA('ScrollingFrame') then
                    local manual=V2.new(pixels(p.CanvasSize.X,size.X,scale),pixels(p.CanvasSize.Y,size.Y,scale)):Max(size)
                    canvases[object]=V2.new(if automatic(p.AutomaticCanvasSize,1) then math.max(manual.X,demand.X) else manual.X,
                        if automatic(p.AutomaticCanvasSize,2) then math.max(manual.Y,demand.Y) else manual.Y)
                end
                return node
            end
            measure(root,rootSize,rootScale,nil,true)
            if not unsettled then
                local function place(object,position,rotation)
                    local node=nodes[object];node.position=position;node.absoluteRotation=rotation+node.rotation
                    local scroll=if object:IsA('ScrollingFrame') then props(object).CanvasPosition*node.scale else V2.zero
                    for _,child in object:GetChildren() do
                        if nodes[child] then place(child,position+nodes[child].relative-scroll,node.absoluteRotation) end
                    end
                end
                nodes[root].rotation=rootRotation
                place(root,rootPosition,0)
                final={revision=initialRevision,nodes=nodes,layouts=layouts,canvases=canvases};break
            end
            seeds=nextSeeds
        end
        assert(final,'AutomaticSize has a cyclic or non-converging size dependency')
        caches[root]=final;return final
    end
    function R.uiRect(object)
        local root=rootOf(object)
        if not root then return rawRect(object) end
        local node=solve(root).nodes[object]
        if not node then return rawRect(object) end
        return node.position,node.size,node.scale,node.absoluteRotation
    end
    function R.uiCanvasSize(object)
        local root=rootOf(object);return root and solve(root).canvases[object] or V2.zero
    end
    local function layoutState(object)
        local root=rootOf(object)
        return root and solve(root).layouts[object] or {content=V2.zero,cellSize=V2.zero,cellCount=V2.zero}
    end
    R.classGetters.UIGridStyleLayout={AbsoluteContentSize=function(self) return layoutState(self).content end}
    R.classGetters.UIGridLayout={AbsoluteCellSize=function(self) return layoutState(self).cellSize end,
        AbsoluteCellCount=function(self) return layoutState(self).cellCount end}
    R.classMethods.UIGridStyleLayout={ApplyLayout=function(self)
        revision+=1;local root=rootOf(self);if root then solve(root) end
    end,SetCustomSortFunction=function(self,callback)
        assert(callback==nil or type(callback)=='function','Expected function or nil');custom[self]=callback;revision+=1
    end}
    for _,name in {'UIGridStyleLayout','UILayout','UIComponent'} do R.noncreatable[name]=true end
end
