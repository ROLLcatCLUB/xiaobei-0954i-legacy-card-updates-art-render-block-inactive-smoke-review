(function (root) {
  "use strict";

  const ACTIONS = ["采纳", "精修", "追问", "重生成", "锁定", "回填上下文", "标记为待确认", "暂不采用"];

  const cards = [
    ["topic_understanding", "课题理解", "苏少版三年级美术《青绿中国色》，40分钟，综合·探索课型。", "二次修订版 header / 教材版本 / 课时时长 / 课型", ["教材版本", "课题", "课时", "课型", "授课班级", "公开课要求"], "needs_confirmation"],
    ["teaching_objectives", "教学目标", "目标包含颜色辨认、设色顺序、对比观察和传统色彩体验。", "教学目标", ["目标维度", "可观测动词", "评价证据", "课标对应"], "draft"],
    ["key_difficult_points", "重难点", "重点是颜色辨识和远山淡近山浓；难点是分层设色顺序和迁移实践。", "教学重难点", ["教学重点", "教学难点", "突破策略"], "draft"],
    ["qinglv_color_rule", "青绿设色规律", "当前规则是远山淡、近山浓，以及赭石打底、石绿罩染、石青点染、藤黄提亮。", "教学目标 / 教学重难点 / 课堂流程", ["色彩规律", "材料依据", "示范步骤", "学生可理解口诀"], "needs_confirmation"],
    ["classroom_flow", "课堂流程", "6个环节：导入、认识矿物色、探究规律、示范、创作、展示评价。", "课堂流程", ["环节名称", "时间", "教师行为", "学生活动", "系统支持"], "draft"],
    ["teacher_questions", "教师关键提问", "包含主色调、远近颜色、点缀色、设色顺序和作品反思等6个问题。", "教师关键提问", ["问题文本", "追问层级", "对应环节", "预期学生回答"], "draft"],
    ["student_activities", "学生活动", "活动包括颜色连连看、色彩观察记录、口诀判断、分层设色创作、一赞一问互评。", "学生活动", ["活动名称", "材料", "分组方式", "完成标准", "系统入口"], "draft"],
    ["board_screen_design", "板书 / 大屏设计", "板书聚焦三种颜色、远近规律和设色顺序；大屏包含课题、颜料、长卷、局部对比、步骤和评价示例。", "板书/大屏设计", ["板书布局", "大屏页码", "图片素材", "是否生成PPT"], "needs_confirmation"],
    ["evaluation_design", "评价方式", "包含过程性观察量表、作品等级标准和学生自评栏。", "评价方式", ["观察点", "等级标准", "自评栏", "互评方式", "是否接过程性评价"], "draft"],
    ["risks_adjustments", "风险与调整", "覆盖颜色混淆、时间不足、操作顺序、颜料蘸取、多媒体故障等课堂风险。", "可能问题与调整", ["问题", "调整策略", "备选材料", "课前准备"], "draft"],
    ["xiaobei_self_check", "小备自查", "R2 自评认为目标可观测、流程可上课、提问有层次、评价形成闭环、风险策略清晰。", "质量自评 / agent_call_2_self_review", ["自查项", "证据", "风险等级", "待确认项"], "needs_confirmation"],
    ["next_refinement", "下一步精修建议", "建议录制示范微视频、设计分层任务、联动语文或历史拓展《千里江山图》文化背景。", "后续精修建议", ["精修方向", "优先级", "需要的素材", "是否生成配套物"], "draft"]
  ].map(([card_id, card_title, teacher_visible_summary, source_from_r2, editable_fields, status]) => ({
    card_id,
    card_title,
    teacher_visible_summary,
    source_from_r2,
    editable_fields,
    status,
    lock_state: false,
    needs_teacher_confirmation: status === "needs_confirmation",
    available_actions: ACTIONS.slice()
  }));

  const followupQuestions = [
    "这个班三年级学生之前接触过中国画设色或水墨材料吗？如果没有，我会把矿物色介绍和操作步骤再降一点难度。",
    "这节课确认是 40 分钟吗？如果是公开课或展示课，我建议压缩颜料来源讲解，把时间让给创作和展示。",
    "这节《青绿中国色》是否要采用长卷取景？如果要，我会把课堂流程改成先取景、再线稿、再青绿设色。",
    "学生是否已有线稿，还是课堂中现场起稿？这会决定 12 分钟创作环节是否够用。",
    "需要接入线稿画板吗？如果接，我会把“设色练习”拆成线稿选择、设色层、提交三个步骤。",
    "本课要不要加入作品提交和高光展厅？如果要，我会把展示评价从 3 分钟改成“提交、筛选、点评、回看”的闭环。",
    "是否需要过程性评价记录？比如记录学生是否完成颜色识别、设色顺序、作品提交和互评。",
    "这节课是否要贴合教研员或公开课要求？如果有要求，请给我关键词，我会调整目标、问题链和评价证据。",
    "是否需要改成公开课版本？公开课版本我会强化问题链、学生表达、作品展示和课堂节奏。",
    "需要我继续生成 PPT、学习单或板书稿吗？可以优先从大屏6页和观察记录表开始。"
  ];

  root.XIAOBEI_AGENT_OUTPUT_EXISTING_WORKBENCH_FIXTURE_0952F_R1 = {
    stage_id: "0952F_R1_EXISTING_WORKBENCH_RUNTIME_INTEGRATION_SPIKE",
    source_agent_stage: "0952B_R2_AGENT_CAPABILITY_CHAINED_RETRY",
    source_review_stage: "0952C_AGENT_OUTPUT_PRODUCT_EXPERIENCE_REVIEW",
    candidate: {
      candidate_id: "lesson_design_cards_candidate_0952F_R1_qinglv",
      candidate_type: "lesson_design_cards_candidate",
      topic: "青绿中国色",
      grade: "三年级",
      subject: "美术",
      design_scope: "lesson",
      candidate_text: "0952B_R2 真实 Agent 输出已拆成 12 张工作台卡片，等待老师逐项确认。",
      status: "ready_for_teacher_review",
      provider_called_in_0952F_R1: false,
      card_update_payload: {
        card_id: "lesson_design_cards_candidate",
        teacher_title: "青绿中国色 · 真实 Agent 输出工作台",
        teacher_summary: "这不是新生成内容，而是把 0952B_R2 的真实输出注入现有小备工作台。",
        status: "ready_for_teacher_review",
        requires_teacher_acceptance: true,
        locked_target: false
      }
    },
    cards,
    followup_questions: followupQuestions,
    safety_flags: {
      provider_called: false,
      new_generation_performed: false,
      runner_executed: false,
      endpoint_created: false,
      memory_read: false,
      memory_write: false,
      feishu_writeback: false,
      formal_scoring: false,
      formal_export: false,
      server_deploy: false,
      seal_allowed: false
    }
  };
})(window);
